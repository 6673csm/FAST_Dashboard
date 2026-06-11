"""
FAST Dashboard - FastAPI Backend
routers/forecast.py: Future forecasting endpoints
"""

import json
import io
import os
import warnings
warnings.filterwarnings("ignore")

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import pandas as pd
import numpy as np
import joblib
from datetime import timedelta
from sklearn.preprocessing import StandardScaler

from database import get_db, Dataset, TrainedModel, User
from auth import get_current_user

router = APIRouter(prefix="/api/forecast", tags=["forecast"])

MODELS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "models")


def _create_features(df: pd.DataFrame) -> pd.DataFrame:
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
    return feature_df.dropna()


def _extrapolate_signals(df: pd.DataFrame, n_days: int, method: str) -> pd.DataFrame:
    signal_cols = ["me-fea", "me-ang", "me-sad"]
    date_col = "date" if "date" in df.columns else df.columns[0]
    last_date = pd.to_datetime(df[date_col]).max()
    future_dates = pd.date_range(start=last_date + timedelta(days=1), periods=n_days, freq="D")
    future_data = {"date": future_dates}

    for col in signal_cols:
        if col in df.columns:
            if method == "last_value":
                future_data[col] = df[col].iloc[-1]
            elif method == "moving_average":
                future_data[col] = df[col].tail(30).mean()
            elif method == "trend":
                recent = df[col].tail(60).values
                x = np.arange(len(recent))
                coeffs = np.polyfit(x, recent, 1)
                fx = np.arange(len(recent), len(recent) + n_days)
                vals = np.clip(np.polyval(coeffs, fx), 0, 1)
                future_data[col] = vals

    return pd.DataFrame(future_data)


@router.post("/run")
def run_forecast(
    payload: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    dataset_id = payload.get("dataset_id")
    model_name = payload.get("model_name", "XGBoost")
    target = payload.get("target", "gh-death")
    n_days = int(payload.get("n_days", 90))
    method = payload.get("extrapolation_method", "moving_average")
    population = int(payload.get("population", 1_000_000))

    d = db.query(Dataset).filter(Dataset.id == dataset_id, Dataset.user_id == current_user.id).first()
    if not d:
        raise HTTPException(status_code=404, detail="Dataset not found")

    df = pd.read_json(io.StringIO(d.data_json), orient="records")

    # Load model & scaler
    model_path = os.path.join(MODELS_DIR, f"{model_name.replace(' ', '_')}_{current_user.id}_{dataset_id}_{target}.pkl")
    scaler_path = os.path.join(MODELS_DIR, f"scaler_{current_user.id}_{dataset_id}_{target}.pkl")

    if not os.path.exists(model_path) or not os.path.exists(scaler_path):
        raise HTTPException(status_code=404, detail="Model not found. Train it first.")

    model = joblib.load(model_path)
    scaler_data = joblib.load(scaler_path)
    scaler: StandardScaler = scaler_data["scaler"]
    feature_names: list = scaler_data["feature_names"]

    # Extrapolate signals
    future_signals = _extrapolate_signals(df, n_days, method)

    # Build future features
    combined = pd.concat([df[["date", "me-fea", "me-ang", "me-sad"]].tail(60), future_signals], ignore_index=True)
    combined_features = _create_features(combined)
    future_features = combined_features.tail(n_days)

    for feat in feature_names:
        if feat not in future_features.columns:
            future_features[feat] = 0.0
    future_features = future_features[feature_names]

    # Scale & predict
    X_scaled = scaler.transform(future_features)
    predicted_rates = model.predict(X_scaled)
    predicted_cases = np.round((predicted_rates * population) / 100_000).astype(int)

    # Summary
    hist_avg = float(df[target].mean() * population / 100_000)
    fc_avg = float(predicted_cases.mean())
    change_pct = ((fc_avg - hist_avg) / max(hist_avg, 1)) * 100
    trend = "increase" if change_pct > 0 else "decrease"
    summary = (
        f"**Forecast**: {n_days} days | Model: {model_name} | Target: {target.upper()}\n\n"
        f"- Avg daily cases: **{fc_avg:.0f}**\n"
        f"- Historical avg: **{hist_avg:.0f}**\n"
        f"- Trend: **{abs(change_pct):.1f}% {trend}** vs historical"
    )

    return {
        "dates": [str(d) for d in future_signals["date"]],
        "predicted_rates": [round(float(r), 6) for r in predicted_rates],
        "predicted_cases": [int(c) for c in predicted_cases],
        "me_fea": [round(float(v), 4) for v in future_signals["me-fea"]],
        "me_ang": [round(float(v), 4) for v in future_signals["me-ang"]],
        "me_sad": [round(float(v), 4) for v in future_signals["me-sad"]],
        "summary": summary,
    }
