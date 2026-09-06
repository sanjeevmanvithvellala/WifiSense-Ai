"""
Historical Predictions API Endpoints.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.app.core.database import get_db
from backend.app.models.entities import PredictionRecord
from backend.app.schemas.schemas import PredictionOut

router = APIRouter()


@router.get("", response_model=List[PredictionOut])
def list_predictions(
    limit: int = Query(50, ge=1, le=500),
    environment: Optional[str] = None,
    activity: Optional[str] = None,
    only_anomalies: bool = False,
    db: Session = Depends(get_db)
):
    """Queries prediction history with filtering."""
    query = db.query(PredictionRecord)
    if environment:
        query = query.filter(PredictionRecord.environment_type == environment)
    if activity:
        query = query.filter(PredictionRecord.activity == activity)
    if only_anomalies:
        query = query.filter(PredictionRecord.is_anomaly == True)

    return query.order_by(PredictionRecord.timestamp.desc()).limit(limit).all()
