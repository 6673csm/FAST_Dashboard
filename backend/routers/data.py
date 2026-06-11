"""
FAST Dashboard - FastAPI Backend
routers/data.py: CSV upload and dataset management endpoints
"""

import json
import io
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
import pandas as pd
import numpy as np

from database import get_db, Dataset, User
from auth import get_current_user
from schemas import DataSummaryOut

router = APIRouter(prefix="/api/data", tags=["data"])


def _serialize_metadata(meta: dict) -> dict:
    """Convert metadata to JSON-serializable form."""
    result = {}
    for k, v in meta.items():
        if isinstance(v, (pd.Timestamp,)):
            result[k] = str(v)
        elif isinstance(v, tuple):
            result[k] = [str(x) for x in v]
        elif isinstance(v, (np.integer,)):
            result[k] = int(v)
        elif isinstance(v, (np.floating,)):
            result[k] = float(v)
        else:
            result[k] = v
    return result


@router.post("/upload", response_model=DataSummaryOut)
async def upload_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Upload a CSV file, auto-clean it, store in DB, return metadata."""
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")

    contents = await file.read()
    try:
        df = pd.read_csv(io.BytesIO(contents))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not parse CSV: {e}")

    original_rows, original_cols = df.shape

    # Clean column names
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

    # Parse date column
    date_cols = [c for c in df.columns if "date" in c]
    if date_cols:
        df[date_cols[0]] = pd.to_datetime(df[date_cols[0]], errors="coerce")
        df = df.sort_values(date_cols[0]).reset_index(drop=True)

    # Handle missing values
    missing_before = int(df.isnull().sum().sum())
    df = df.ffill()
    for col in df.select_dtypes(include=[np.number]).columns:
        df[col] = df[col].fillna(df[col].mean())
    df = df.dropna(thresh=int(len(df.columns) * 0.7))
    missing_after = int(df.isnull().sum().sum())

    required_cols = ["date", "me-fea", "me-ang", "me-sad", "gh-death", "gh-injure"]
    missing_required = [c for c in required_cols if c not in df.columns]

    # Quality score
    score = 100.0
    score -= len(missing_required) * 15
    mp = (df.isnull().sum().sum() / max(df.size, 1)) * 100
    score -= mp * 2
    dup_pct = (df.duplicated().sum() / max(len(df), 1)) * 100
    score -= dup_pct * 1.5
    quality_score = float(max(0, min(100, score)))

    date_range = None
    if date_cols and pd.api.types.is_datetime64_any_dtype(df[date_cols[0]]):
        date_range = [str(df[date_cols[0]].min()), str(df[date_cols[0]].max())]

    metadata = {
        "source": file.filename,
        "original_rows": original_rows,
        "original_cols": original_cols,
        "cleaned_rows": len(df),
        "cleaned_cols": len(df.columns),
        "missing_values_before": missing_before,
        "missing_values_after": missing_after,
        "data_quality_score": quality_score,
        "date_range": date_range,
        "missing_required_cols": missing_required,
    }

    # Convert datetime columns for JSON serialization
    df_for_json = df.copy()
    for col in df_for_json.select_dtypes(include=["datetime64[ns]", "datetime64[ns, UTC]"]).columns:
        df_for_json[col] = df_for_json[col].astype(str)

    dataset = Dataset(
        user_id=current_user.id,
        filename=file.filename,
        data_json=df_for_json.to_json(orient="records"),
        metadata_json=json.dumps(metadata),
    )
    db.add(dataset)
    db.commit()
    db.refresh(dataset)

    preview = json.loads(df_for_json.head(10).to_json(orient="records"))

    return DataSummaryOut(
        filename=file.filename,
        original_rows=original_rows,
        cleaned_rows=len(df),
        original_cols=original_cols,
        cleaned_cols=len(df.columns),
        missing_values_before=missing_before,
        missing_values_after=missing_after,
        data_quality_score=quality_score,
        date_range=date_range,
        missing_required_cols=missing_required,
        columns=list(df.columns),
        preview=preview,
    )


@router.get("/list")
def list_datasets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all datasets for the current user."""
    datasets = db.query(Dataset).filter(Dataset.user_id == current_user.id).all()
    return [
        {
            "id": d.id,
            "filename": d.filename,
            "metadata": json.loads(d.metadata_json),
            "created_at": str(d.created_at),
        }
        for d in datasets
    ]


@router.get("/{dataset_id}/summary")
def dataset_summary(
    dataset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get summary and preview for a specific dataset."""
    d = db.query(Dataset).filter(
        Dataset.id == dataset_id, Dataset.user_id == current_user.id
    ).first()
    if not d:
        raise HTTPException(status_code=404, detail="Dataset not found")

    df = pd.read_json(io.StringIO(d.data_json), orient="records")
    meta = json.loads(d.metadata_json)
    preview = json.loads(df.head(10).to_json(orient="records"))

    return {
        "id": d.id,
        "filename": d.filename,
        "metadata": meta,
        "columns": list(df.columns),
        "preview": preview,
        "stats": json.loads(df.describe().round(4).to_json()),
    }


@router.delete("/{dataset_id}")
def delete_dataset(
    dataset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a dataset."""
    d = db.query(Dataset).filter(
        Dataset.id == dataset_id, Dataset.user_id == current_user.id
    ).first()
    if not d:
        raise HTTPException(status_code=404, detail="Dataset not found")
    db.delete(d)
    db.commit()
    return {"detail": "Dataset deleted"}
