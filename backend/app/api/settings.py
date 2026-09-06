"""
System Settings and Platform Configuration API Endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, List
from backend.app.core.database import get_db
from backend.app.models.entities import SystemSetting

router = APIRouter()


@router.get("")
def get_all_settings(db: Session = Depends(get_db)):
    """Returns all system configuration settings."""
    settings = db.query(SystemSetting).all()
    return {s.key: {"value": s.value, "description": s.description} for s in settings}


@router.post("")
def update_settings(payload: Dict[str, Any], db: Session = Depends(get_db)):
    """Updates one or more system settings."""
    for key, val in payload.items():
        s = db.query(SystemSetting).filter(SystemSetting.key == key).first()
        if s:
            s.value = val
        else:
            db.add(SystemSetting(key=key, value=val, description="Custom Setting"))
    db.commit()
    return {"status": "success", "message": "Settings updated successfully."}
