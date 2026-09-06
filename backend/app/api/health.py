"""
Health Check and System Diagnostics Endpoint.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from backend.app.core.database import get_db
from ml.experiments.metrics import get_system_resource_usage
from ml.inference.engine import default_inference_engine
from backend.app.websocket.manager import manager
import time

router = APIRouter()


@router.get("/health")
def get_health_status(db: Session = Depends(get_db)):
    """Returns comprehensive health check for all subsystem components."""
    # Database check
    db_ok = True
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        db_ok = False

    # ML Engine check
    ml_ok = (
        default_inference_engine.classifier is not None
        and default_inference_engine.classifier.is_trained
    )

    resources = get_system_resource_usage()

    return {
        "status": "healthy" if db_ok and ml_ok else "degraded",
        "timestamp": time.time(),
        "services": {
            "backend": "online",
            "database": "online" if db_ok else "offline",
            "ml_engine": "ready" if ml_ok else "initializing",
            "websocket": "active",
            "active_ws_connections": len(manager.active_connections),
        },
        "system_resources": resources,
        "active_classifier": default_inference_engine.classifier.name if default_inference_engine.classifier else "None",
        "active_anomaly_detector": default_inference_engine.anomaly_detector.name if default_inference_engine.anomaly_detector else "None",
    }
