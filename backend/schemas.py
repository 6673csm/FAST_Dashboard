"""
FAST Dashboard - FastAPI Backend
schemas.py: Pydantic request/response models
"""

from pydantic import BaseModel, EmailStr
from typing import Optional, Any, Dict, List
from datetime import datetime


# ── Auth ──────────────────────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str


class UserOut(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime

    class Config:
        from_attributes = True


# ── Data ──────────────────────────────────────────────────────────────────────

class DatasetMetaOut(BaseModel):
    id: int
    filename: str
    metadata: Dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True


class DataSummaryOut(BaseModel):
    filename: str
    original_rows: int
    cleaned_rows: int
    original_cols: int
    cleaned_cols: int
    missing_values_before: int
    missing_values_after: int
    data_quality_score: float
    date_range: Optional[List[str]]
    missing_required_cols: List[str]
    columns: List[str]
    preview: List[Dict[str, Any]]   # first 10 rows


# ── Models (ML) ───────────────────────────────────────────────────────────────

class TrainRequest(BaseModel):
    dataset_id: int
    target: str  # "gh-death" or "gh-injure"


class ModelResultOut(BaseModel):
    model_name: str
    status: str
    training_time: float
    metrics: Optional[Dict[str, float]]


class TrainResultsOut(BaseModel):
    target: str
    results: List[ModelResultOut]


class FeatureImportanceOut(BaseModel):
    model_name: str
    target: str
    features: List[Dict[str, Any]]  # [{feature, importance}]


# ── Forecast ──────────────────────────────────────────────────────────────────

class ForecastRequest(BaseModel):
    dataset_id: int
    model_name: str
    target: str
    n_days: int = 90
    extrapolation_method: str = "moving_average"  # last_value | moving_average | trend
    population: int = 1_000_000


class ForecastOut(BaseModel):
    dates: List[str]
    predicted_rates: List[float]
    predicted_cases: List[int]
    me_fea: List[float]
    me_ang: List[float]
    me_sad: List[float]
    summary: str


# ── Simulator ─────────────────────────────────────────────────────────────────

class SimulatorRequest(BaseModel):
    dataset_id: int
    model_name: str
    target: str
    fear_delta: float = 0.0     # % change to fear signal
    anger_delta: float = 0.0    # % change to anger signal
    sadness_delta: float = 0.0  # % change to sadness signal


class SimulatorOut(BaseModel):
    baseline_avg: float
    simulated_avg: float
    pct_change: float
    dates: List[str]
    baseline: List[float]
    simulated: List[float]


# ── Reports ───────────────────────────────────────────────────────────────────

class ReportOut(BaseModel):
    content: str  # Markdown text
