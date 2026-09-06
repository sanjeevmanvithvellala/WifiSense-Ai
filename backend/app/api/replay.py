"""
Replay Control and Streaming Configuration API Endpoints.
"""

from fastapi import APIRouter, HTTPException
from backend.app.schemas.schemas import ReplayControlRequest
from backend.app.websocket.replay import replay_streamer
from ml.synthetic_generator import DEMO_ACTIVITIES, ENVIRONMENT_PROFILES
from ml.adapters.registry import default_adapter_registry

from backend.app.services.live_ingest import live_hardware_ingest_server
from backend.app.services.pc_wifi_probe import pc_local_wifi_probe

router = APIRouter()


@router.post("/control")
def control_replay(req: ReplayControlRequest):
    """Controls the live CSI replay streamer (play, pause, stop, reset, hardware UDP, PC Wi-Fi)."""
    action = req.action.lower()
    source_mode = getattr(req, "source_mode", "synthetic") or "synthetic"
    
    if action == "play" or action == "start":
        if source_mode == "hardware_udp":
            replay_streamer.stop()
            pc_local_wifi_probe.stop()
            live_hardware_ingest_server.start()
            return {
                "status": "listening_udp",
                "source_mode": "hardware_udp",
                "message": "Live Hardware UDP Ingestion Server running on port 5555. Streaming incoming packets.",
                "state": {"is_running": True, "source_mode": "hardware_udp"}
            }
        elif source_mode == "pc_wifi":
            replay_streamer.stop()
            live_hardware_ingest_server.stop()
            pc_local_wifi_probe.start()
            return {
                "status": "probing_pc_wifi",
                "source_mode": "pc_wifi",
                "message": "Local PC Wi-Fi Probe active. Polling real-time link fluctuations from home Wi-Fi adapter.",
                "state": {"is_running": True, "source_mode": "pc_wifi"}
            }
        else:
            live_hardware_ingest_server.stop()
            pc_local_wifi_probe.stop()
            replay_streamer.start(
                dataset_id=req.dataset_id,
                environment=req.environment_type,
                activity=req.activity_scenario or "Walking",
                playback_speed=req.playback_speed,
                add_anomaly=req.add_anomaly
            )
            return {
                "status": "playing",
                "source_mode": "synthetic",
                "state": {
                    "dataset_id": req.dataset_id,
                    "environment": req.environment_type,
                    "activity": req.activity_scenario,
                    "playback_speed": req.playback_speed,
                    "add_anomaly": req.add_anomaly,
                    "is_running": True,
                    "is_paused": False
                }
            }

    elif action == "pause":
        replay_streamer.pause()
        return {"status": "paused", "is_running": True, "is_paused": True}

    elif action == "resume":
        replay_streamer.resume()
        return {"status": "playing", "is_running": True, "is_paused": False}

    elif action == "stop" or action == "reset":
        replay_streamer.stop()
        live_hardware_ingest_server.stop()
        pc_local_wifi_probe.stop()
        return {"status": "stopped", "is_running": False, "is_paused": False}

    else:
        raise HTTPException(status_code=400, detail=f"Unknown replay action '{action}'. Use play, pause, resume, or stop.")


@router.get("/status")
def get_replay_status():
    """Returns the current state of the replay streamer."""
    return {
        "is_running": replay_streamer.is_running,
        "is_paused": replay_streamer.is_paused,
        "dataset_id": replay_streamer.current_dataset,
        "environment": replay_streamer.current_environment,
        "activity": replay_streamer.current_activity,
        "playback_speed": replay_streamer.playback_speed,
        "add_anomaly": replay_streamer.add_anomaly,
        "demo_activities": DEMO_ACTIVITIES,
        "environments": list(ENVIRONMENT_PROFILES.keys())
    }
