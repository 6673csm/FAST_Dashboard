"""
FAST Dashboard - FastAPI Backend
routers/reports.py: Report generation endpoint
"""

import json
import io
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session
from datetime import datetime

from database import get_db, Dataset, TrainedModel, User
from auth import get_current_user

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.get("/generate/{dataset_id}", response_class=PlainTextResponse)
def generate_report(
    dataset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate a markdown report for a dataset and its trained models."""
    d = db.query(Dataset).filter(Dataset.id == dataset_id, Dataset.user_id == current_user.id).first()
    if not d:
        raise HTTPException(status_code=404, detail="Dataset not found")

    meta = json.loads(d.metadata_json)
    models = db.query(TrainedModel).filter(
        TrainedModel.dataset_id == dataset_id, TrainedModel.user_id == current_user.id
    ).all()

    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    report = f"""# FAST Dashboard — Analysis Report
**Generated:** {now}  
**User:** {current_user.username}  
**Dataset:** {d.filename}

---

## 1. Dataset Summary

| Metric | Value |
|---|---|
| Original Rows | {meta.get('original_rows', 'N/A')} |
| Cleaned Rows | {meta.get('cleaned_rows', 'N/A')} |
| Original Columns | {meta.get('original_cols', 'N/A')} |
| Cleaned Columns | {meta.get('cleaned_cols', 'N/A')} |
| Missing Values (Before) | {meta.get('missing_values_before', 'N/A')} |
| Missing Values (After) | {meta.get('missing_values_after', 'N/A')} |
| Data Quality Score | {meta.get('data_quality_score', 0):.1f}% |

**Date Range:** {meta.get('date_range', ['N/A', 'N/A'])}

**Missing Required Columns:** {', '.join(meta.get('missing_required_cols', [])) or 'None'}

---

## 2. Model Performance

"""

    if models:
        # Group by target
        targets = {}
        for m in models:
            targets.setdefault(m.target, []).append(m)

        for target, target_models in targets.items():
            report += f"### Target: `{target}`\n\n"
            report += "| Model | MAE | RMSE | R² | MAPE (%) |\n"
            report += "|---|---|---|---|---|\n"
            for m in target_models:
                mx = json.loads(m.metrics_json) if m.metrics_json else {}
                report += (
                    f"| {m.model_name} | "
                    f"{mx.get('mae', 'N/A')} | "
                    f"{mx.get('rmse', 'N/A')} | "
                    f"{mx.get('r2', 'N/A')} | "
                    f"{mx.get('mape', 'N/A')} |\n"
                )
            report += "\n"
    else:
        report += "_No models trained yet for this dataset._\n\n"

    report += """---

## 3. System Notes

> ⚠️ This system predicts **aggregate national trends only** — NOT individual risk assessment.  
> Predictions are based on social media mental health signals (Fear, Anger, Sadness).  
> Use findings to inform policy decisions, not clinical judgments.

---

*FAST Dashboard v2.0 — Full-Stack Edition*
"""
    return report
