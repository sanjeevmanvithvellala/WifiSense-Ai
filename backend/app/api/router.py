"""
Main API Router for WiFiSense AI Backend.
"""

from fastapi import APIRouter
from backend.app.api import (
    health,
    environments,
    datasets,
    models,
    experiments,
    predictions,
    events,
    analytics,
    settings,
    replay,
)

api_router = APIRouter()

api_router.include_router(health.router, tags=["Health"])
api_router.include_router(environments.router, prefix="/environments", tags=["Environments"])
api_router.include_router(datasets.router, prefix="/datasets", tags=["Datasets"])
api_router.include_router(models.router, prefix="/models", tags=["Models"])
api_router.include_router(experiments.router, prefix="/experiments", tags=["Experiments"])
api_router.include_router(predictions.router, prefix="/predictions", tags=["Predictions"])
api_router.include_router(events.router, prefix="/events", tags=["Events"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
api_router.include_router(settings.router, prefix="/settings", tags=["Settings"])
api_router.include_router(replay.router, prefix="/replay", tags=["Replay"])
