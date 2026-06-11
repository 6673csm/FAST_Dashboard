"""
FAST Dashboard - FastAPI Backend
routers/models.py: AutoML training and evaluation endpoints
"""

import json
import io
import os
import time
import warnings
warnings.filterwarnings("ignore")

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import BayesianRidge
from sklearn.svm import SVR
from xgboost import XGBRegressor
from statsmodels.tsa.arima.model import ARIMA
import joblib

from database import get_db, Dataset, TrainedModel, User
from auth import get_current_user

router = APIRouter(prefix="/api/models", tags=["models"])

MODELS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "models")
os.makedirs(MODELS_DIR, exist_ok=True)


def _create_features(df: pd.DataFrame) -> pd.DataFrame:
    """Create lag and rolling features from signals."""
    feature_df = pd.DataFrame()
    signal_cols = ["me-fea", "me-ang", "me-sad"]
    for col in signal_cols:
        if col in df.columns:
            feature_df[col] = df[col]
            for lag in [1, 7, 14, 30]:
                feature_df[f"{col}_lag{lag}"] = df[col].shift(lag)
            for window in [7, 30]:
                feature_df[f"{col}_ma{window}"] = df[col].rolling(window).mean()
                feature_df[f"{col}_std{window}"] = df[col].rolling(window).std()
    feature_df = feature_df.dropna()
    return feature_df


def _compute_metrics(y_true, y_pred) -> dict:
    mae = float(mean_absolute_error(y_true, y_pred))
    rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
    r2 = float(r2_score(y_true, y_pred))
    mape = float(np.mean(np.abs((y_true - y_pred) / np.maximum(np.abs(y_true), 1e-8))) * 100)
    return {"mae": round(mae, 4), "rmse": round(rmse, 4), "r2": round(r2, 4), "mape": round(mape, 4)}


@router.post("/train")
def train_models(
    payload: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Train all AutoML models for a given target variable."""
    dataset_id = payload.get("dataset_id")
    target = payload.get("target", "gh-death")

    d = db.query(Dataset).filter(
        Dataset.id == dataset_id, Dataset.user_id == current_user.id
    ).first()
    if not d:
        raise HTTPException(status_code=404, detail="Dataset not found")

    df = pd.read_json(io.StringIO(d.data_json), orient="records")

    if target not in df.columns:
        raise HTTPException(status_code=400, detail=f"Column '{target}' not found in dataset")

    # Build features
    features_df = _create_features(df)
    y = df[target].loc[features_df.index]
    X = features_df

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, shuffle=False)
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    scaler_path = os.path.join(MODELS_DIR, f"scaler_{current_user.id}_{dataset_id}_{target}.pkl")
    joblib.dump({"scaler": scaler, "feature_names": list(X.columns)}, scaler_path)

    model_configs = {
        "Random Forest": RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1),
        "XGBoost": XGBRegressor(n_estimators=100, learning_rate=0.1, max_depth=6, random_state=42, n_jobs=-1, verbosity=0),
        "SVR": SVR(kernel="rbf", C=1.0, gamma="auto"),
        "Bayesian Ridge": BayesianRidge(max_iter=300),
    }

    all_results = []

    for name, model in model_configs.items():
        try:
            t0 = time.time()
            model.fit(X_train_scaled, y_train)
            elapsed = round(time.time() - t0, 3)
            preds = model.predict(X_test_scaled)
            metrics = _compute_metrics(y_test.values, preds)

            # Save model
            model_path = os.path.join(MODELS_DIR, f"{name.replace(' ', '_')}_{current_user.id}_{dataset_id}_{target}.pkl")
            joblib.dump(model, model_path)

            # Persist to DB
            tm = TrainedModel(
                user_id=current_user.id,
                dataset_id=dataset_id,
                model_name=name,
                target=target,
                metrics_json=json.dumps(metrics),
                model_path=model_path,
            )
            db.add(tm)

            all_results.append({"model_name": name, "status": "success", "training_time": elapsed, "metrics": metrics})

        except Exception as e:
            all_results.append({"model_name": name, "status": f"failed: {e}", "training_time": 0, "metrics": {}})

    # ARIMA
    try:
        t0 = time.time()
        arima_model = ARIMA(y_train, order=(1, 1, 1)).fit()
        elapsed = round(time.time() - t0, 3)
        arima_preds = arima_model.forecast(steps=len(y_test))
        metrics = _compute_metrics(y_test.values, arima_preds)

        arima_path = os.path.join(MODELS_DIR, f"ARIMA_{current_user.id}_{dataset_id}_{target}.pkl")
        joblib.dump(arima_model, arima_path)

        tm = TrainedModel(user_id=current_user.id, dataset_id=dataset_id, model_name="ARIMA", target=target, metrics_json=json.dumps(metrics), model_path=arima_path)
        db.add(tm)
        all_results.append({"model_name": "ARIMA", "status": "success", "training_time": elapsed, "metrics": metrics})
    except Exception as e:
        all_results.append({"model_name": "ARIMA", "status": f"failed: {e}", "training_time": 0, "metrics": {}})

    db.commit()
    return {"target": target, "results": all_results}


@router.get("/list/{dataset_id}")
def list_models(
    dataset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all trained models for a dataset."""
    models = db.query(TrainedModel).filter(
        TrainedModel.dataset_id == dataset_id, TrainedModel.user_id == current_user.id
    ).all()
    return [
        {
            "id": m.id,
            "model_name": m.model_name,
            "target": m.target,
            "metrics": json.loads(m.metrics_json) if m.metrics_json else {},
            "created_at": str(m.created_at),
        }
        for m in models
    ]


@router.get("/feature-importance/{dataset_id}/{model_name}/{target}")
def feature_importance(
    dataset_id: int,
    model_name: str,
    target: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get feature importance for a tree-based model."""
    tm = db.query(TrainedModel).filter(
        TrainedModel.dataset_id == dataset_id,
        TrainedModel.model_name == model_name,
        TrainedModel.target == target,
        TrainedModel.user_id == current_user.id,
    ).first()
    if not tm or not tm.model_path or not os.path.exists(tm.model_path):
        raise HTTPException(status_code=404, detail="Model file not found")

    model = joblib.load(tm.model_path)
    scaler_data_path = os.path.join(MODELS_DIR, f"scaler_{current_user.id}_{dataset_id}_{target}.pkl")
    if not os.path.exists(scaler_data_path):
        raise HTTPException(status_code=404, detail="Scaler not found")
    scaler_data = joblib.load(scaler_data_path)
    feature_names = scaler_data["feature_names"]

    if hasattr(model, "feature_importances_"):
        importance = model.feature_importances_
    elif hasattr(model, "coef_"):
        importance = np.abs(model.coef_)
    else:
        return {"features": []}

    total = importance.sum()
    features = [
        {"feature": f, "importance": round(float(i / total * 100), 2)}
        for f, i in sorted(zip(feature_names, importance), key=lambda x: -x[1])
    ]
    return {"model_name": model_name, "target": target, "features": features}
