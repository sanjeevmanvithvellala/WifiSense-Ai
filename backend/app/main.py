"""
WiFiSense AI Backend Main Application.
FastAPI Application providing REST endpoints and WebSocket live CSI replay stream.
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from backend.app.core.config import settings
from backend.app.core.database import engine, Base, SessionLocal
from backend.app.services.seed import seed_database
from backend.app.api.router import api_router
from backend.app.websocket.manager import manager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("wifisense.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown lifecycle handler."""
    logger.info("Initializing WiFiSense AI Database and Services...")
    Base.metadata.create_all(bind=engine)
    
    # Run database seed
    with SessionLocal() as db:
        try:
            seed_database(db)
            logger.info("Database initialized and seeded successfully.")
        except Exception as e:
            logger.error(f"Database seed notice: {e}")

    yield
    logger.info("Shutting down WiFiSense AI...")


app = FastAPI(
    title="WiFiSense AI Backend",
    description="Environment-Agnostic and Privacy-Preserving Human Activity Intelligence Platform Using Wi-Fi CSI",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Open for development dashboard connections
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount REST API Router
app.include_router(api_router, prefix=settings.API_V1_STR)


# WebSocket Replay Endpoint
@app.websocket("/ws/replay")
async def websocket_replay_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time CSI frame and activity intelligence streaming.
    """
    await manager.connect(websocket)
    try:
        while True:
            # Handle incoming client commands over websocket if any
            data = await websocket.receive_text()
            # Echo or process control message
            logger.debug(f"Received WS message: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.warning(f"WebSocket connection error: {e}")
        manager.disconnect(websocket)


@app.get("/")
def root():
    return {
        "project": "WiFiSense AI",
        "description": "Environment-Agnostic and Privacy-Preserving Human Activity Intelligence Platform Using Wi-Fi CSI",
        "status": "Online",
        "api_docs": "/docs",
        "health_check": f"{settings.API_V1_STR}/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host=settings.HOST, port=settings.PORT, reload=True)
