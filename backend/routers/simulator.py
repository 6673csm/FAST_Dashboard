"""
FAST Dashboard - FastAPI Backend
routers/simulator.py: Policy What-If simulation endpoint
"""

import io
import os
import warnings
warnings.filterwarnings("ignore")

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import pandas as pd
import numpy as np
import joblib

from database import get_db, Dataset, User
from auth import get_current_user

router = APIRouter(prefix="/api/simulator", tags=["simulator"])

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


@router.post("/run")
def run_simulation(
    payload: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Run a What-If policy scenario by adjusting signal values."""
    dataset_id = payload.get("dataset_id")
    model_name = payload.get("model_name", "XGBoost")
    target = payload.get("target", "gh-death")
    fear_delta = float(payload.get("fear_delta", 0.0))
    anger_delta = float(payload.get("anger_delta", 0.0))
    sadness_delta = float(payload.get("sadness_delta", 0.0))

    d = db.query(Dataset).filter(Dataset.id == dataset_id, Dataset.user_id == current_user.id).first()
    if not d:
        raise HTTPException(status_code=404, detail="Dataset not found")

    df = pd.read_json(io.StringIO(d.data_json), orient="records")

    model_path = os.path.join(MODELS_DIR, f"{model_name.replace(' ', '_')}_{current_user.id}_{dataset_id}_{target}.pkl")
    scaler_path = os.path.join(MODELS_DIR, f"scaler_{current_user.id}_{dataset_id}_{target}.pkl")

    if not os.path.exists(model_path) or not os.path.exists(scaler_path):
        raise HTTPException(status_code=404, detail="Model not found. Train it first.")

    model = joblib.load(model_path)
    scaler_data = joblib.load(scaler_path)
    scaler = scaler_data["scaler"]
    feature_names = scaler_data["feature_names"]

    # Baseline features
    features = _create_features(df)
    for f in feature_names:
        if f not in features.columns:
            features[f] = 0.0
    features = features[feature_names]

    baseline_preds = model.predict(scaler.transform(features))

    # Simulated: apply deltas to signal columns
    df_sim = df.copy()
    for col, delta in [("me-fea", fear_delta), ("me-ang", anger_delta), ("me-sad", sadness_delta)]:
        if col in df_sim.columns:
            df_sim[col] = np.clip(df_sim[col] * (1 + delta / 100), 0, 1)

    sim_features = _create_features(df_sim)
    for f in feature_names:
        if f not in sim_features.columns:
            sim_features[f] = 0.0
    sim_features = sim_features[feature_names]

    sim_preds = model.predict(scaler.transform(sim_features))

    # Align lengths
    n = min(len(baseline_preds), len(sim_preds))
    baseline_preds = baseline_preds[:n]
    sim_preds = sim_preds[:n]

    date_col = "date" if "date" in df.columns else df.columns[0]
    dates = [str(d) for d in df[date_col].tail(n)]

    baseline_avg = float(np.mean(baseline_preds))
    sim_avg = float(np.mean(sim_preds))
    pct_change = ((sim_avg - baseline_avg) / max(abs(baseline_avg), 1e-8)) * 100

    return {
        "baseline_avg": round(baseline_avg, 4),
        "simulated_avg": round(sim_avg, 4),
        "pct_change": round(pct_change, 2),
        "dates": dates,
        "baseline": [round(float(v), 4) for v in baseline_preds],
        "simulated": [round(float(v), 4) for v in sim_preds],
    }
