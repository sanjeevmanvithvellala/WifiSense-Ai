"""
Activity Intelligence Events API Endpoints.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.app.core.database import get_db
from backend.app.models.entities import EventRecord
from backend.app.schemas.schemas import EventOut

router = APIRouter()


@router.get("", response_model=List[EventOut])
def list_events(
    limit: int = Query(50, ge=1, le=500),
    severity: Optional[str] = None,
    environment: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Queries logged human activity transition and anomaly detection events."""
    query = db.query(EventRecord)
    if severity:
        query = query.filter(EventRecord.severity == severity)
    if environment:
        query = query.filter(EventRecord.environment_type == environment)

    return query.order_by(EventRecord.timestamp.desc()).limit(limit).all()
