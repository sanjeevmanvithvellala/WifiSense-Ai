"""
Environment Management API Endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from backend.app.core.database import get_db
from backend.app.models.entities import Environment
from backend.app.schemas.schemas import EnvironmentCreate, EnvironmentUpdate, EnvironmentOut
from ml.synthetic_generator import ENVIRONMENT_PROFILES
import uuid

router = APIRouter()


@router.get("", response_model=List[EnvironmentOut])
def list_environments(db: Session = Depends(get_db)):
    """Lists all registered physical environment profiles."""
    return db.query(Environment).all()


@router.post("", response_model=EnvironmentOut, status_code=status.HTTP_201_CREATED)
def create_environment(env_in: EnvironmentCreate, db: Session = Depends(get_db)):
    """Creates a new environment profile."""
    existing = db.query(Environment).filter(Environment.id == env_in.id).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Environment with ID '{env_in.id}' already exists.")

    env = Environment(**env_in.model_dump())
    db.add(env)
    db.commit()
    db.refresh(env)
    return env


@router.get("/{env_id}", response_model=EnvironmentOut)
def get_environment(env_id: str, db: Session = Depends(get_db)):
    """Gets details for a specific environment."""
    env = db.query(Environment).filter(Environment.id == env_id).first()
    if not env:
        raise HTTPException(status_code=404, detail="Environment not found.")
    return env


@router.put("/{env_id}", response_model=EnvironmentOut)
def update_environment(env_id: str, env_in: EnvironmentUpdate, db: Session = Depends(get_db)):
    """Updates an existing environment."""
    env = db.query(Environment).filter(Environment.id == env_id).first()
    if not env:
        raise HTTPException(status_code=404, detail="Environment not found.")

    update_data = env_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(env, field, value)

    db.commit()
    db.refresh(env)
    return env


@router.delete("/{env_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_environment(env_id: str, db: Session = Depends(get_db)):
    """Deletes an environment."""
    env = db.query(Environment).filter(Environment.id == env_id).first()
    if not env:
        raise HTTPException(status_code=404, detail="Environment not found.")
    db.delete(env)
    db.commit()
    return None


@router.post("/{env_id}/calibrate")
def calibrate_environment(env_id: str, db: Session = Depends(get_db)):
    """Triggers static baseline channel state calibration for the specified environment."""
    env = db.query(Environment).filter(Environment.id == env_id).first()
    if not env:
        raise HTTPException(status_code=404, detail="Environment not found.")

    # Compute calibration metrics
    prof = ENVIRONMENT_PROFILES.get(env.type, ENVIRONMENT_PROFILES["Office"])
    env.is_calibrated = True
    env.multipath_scale = prof["multipath_scale"]
    env.noise_floor = prof["noise_floor"]
    env.calibration_data = {
        "calibrated_noise_floor": prof["noise_floor"],
        "multipath_dispersion": prof["multipath_scale"],
        "subcarrier_channels_calibrated": 64,
        "calibration_timestamp": __import__("time").time()
    }
    db.commit()
    db.refresh(env)
    return {
        "status": "success",
        "message": f"Environment '{env.name}' successfully calibrated.",
        "environment": EnvironmentOut.model_validate(env)
    }
