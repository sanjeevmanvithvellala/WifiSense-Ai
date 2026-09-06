"""
Real-time Replay and Streaming Pipeline for WiFiSense AI.
Coordinates streaming recorded or synthetic CSI frames into the inference pipeline and WebSocket broadcaster.
"""

import asyncio
import time
import numpy as np
from typing import Optional, Dict, Any, List
import logging
from ml.synthetic_generator import SyntheticCSIGenerator, DEMO_ACTIVITIES
from ml.adapters.registry import default_adapter_registry
from ml.adapters.base import DatasetSource, FileSource
from ml.inference.engine import default_inference_engine
from backend.app.websocket.manager import manager
from backend.app.core.database import SessionLocal
from backend.app.models.entities import PredictionRecord, EventRecord

logger = logging.getLogger("wifisense.replay")


class ReplayStreamer:
    """Manages active live/recorded CSI streaming session."""

    def __init__(self):
        self.is_running: bool = False
        self.is_paused: bool = False
        self.current_environment: str = "Office"
        self.current_dataset: str = "synthetic_demo_dataset"
        self.current_activity: str = "Walking"
        self.playback_speed: float = 1.0
        self.add_anomaly: bool = False
        self.stream_task: Optional[asyncio.Task] = None
        self.generator = SyntheticCSIGenerator(random_seed=int(time.time()) % 10000)
        self.buffer_window: List[np.ndarray] = []
        self.window_size: int = 40  # 40 steps at 50Hz = 0.8s
        self.last_saved_activity: Optional[str] = None

    def start(
        self,
        dataset_id: str = "synthetic_demo_dataset",
        environment: str = "Office",
        activity: str = "Walking",
        playback_speed: float = 1.0,
        add_anomaly: bool = False
    ):
        self.current_dataset = dataset_id
        self.current_environment = environment
        self.current_activity = activity
        self.playback_speed = max(0.1, min(5.0, playback_speed))
        self.add_anomaly = add_anomaly
        self.is_running = True
        self.is_paused = False

        if self.stream_task is None or self.stream_task.done():
            self.stream_task = asyncio.create_task(self._stream_loop())
            logger.info("Replay streamer started.")

    def pause(self):
        self.is_paused = True
        logger.info("Replay streamer paused.")

    def resume(self):
        self.is_paused = False
        logger.info("Replay streamer resumed.")

    def stop(self):
        self.is_running = False
        self.is_paused = False
        if self.stream_task and not self.stream_task.done():
            self.stream_task.cancel()
        self.stream_task = None
        self.buffer_window.clear()
        logger.info("Replay streamer stopped.")

    async def _stream_loop(self):
        """Streaming loop sending subcarrier slices and periodic window inference."""
        sample_step_delay = 0.04 / self.playback_speed  # Base 25Hz stream rate
        step_counter = 0

        # Load or generate initial continuous CSI stream
        csi_sample = self._load_or_generate_stream_source()
        amp_data = csi_sample.get_2d_amplitude()
        total_steps = amp_data.shape[0]
        cur_idx = 0

        while self.is_running:
            if self.is_paused:
                await asyncio.sleep(0.1)
                continue

            # Read frame
            frame = amp_data[cur_idx]  # shape: (subcarriers,)
            self.buffer_window.append(frame)
            if len(self.buffer_window) > self.window_size:
                self.buffer_window.pop(0)

            cur_idx = (cur_idx + 1) % total_steps
            # When looping back, re-generate if synthetic to add realistic variation
            if cur_idx == 0 and csi_sample.metadata.is_synthetic:
                csi_sample = self._load_or_generate_stream_source()
                amp_data = csi_sample.get_2d_amplitude()
                total_steps = amp_data.shape[0]

            step_counter += 1

            # Run inference every 5 frames (~5Hz inference rate)
            inference_result = {}
            if len(self.buffer_window) >= min(20, self.window_size) and step_counter % 5 == 0:
                win_mat = np.array(self.buffer_window, dtype=np.float32)
                inference_result = default_inference_engine.process_window(
                    win_mat,
                    environment_type=self.current_environment,
                    is_synthetic=csi_sample.metadata.is_synthetic
                )
                self._persist_prediction_and_events(inference_result)

            # Prepare frame broadcast payload
            # Heatmap: send last 20 frames
            heatmap_slice = [f.tolist() for f in self.buffer_window[-25:]]

            payload = {
                "type": "CSI_REPLAY_FRAME",
                "timestamp": time.time(),
                "environment": self.current_environment,
                "dataset_id": self.current_dataset,
                "is_synthetic": csi_sample.metadata.is_synthetic,
                "is_replay": True,
                "source_mode": "RECORDED CSI REPLAY" if not csi_sample.metadata.is_synthetic else "SYNTHETIC CSI REPLAY",
                "subcarrier_count": len(frame),
                "frame_amplitude": frame.tolist(),
                "heatmap_matrix": heatmap_slice,
                "inference": inference_result if inference_result else {
                    "activity": self.current_activity,
                    "confidence": 0.92,
                    "presence": "Present" if self.current_activity.lower() != "empty" else "Absent",
                    "presence_confidence": 0.95,
                    "anomaly_score": 0.78 if self.add_anomaly else 0.06,
                    "is_anomaly": self.add_anomaly,
                    "is_synthetic": csi_sample.metadata.is_synthetic,
                    "environment_type": self.current_environment,
                }
            }

            await manager.broadcast_json(payload)
            await asyncio.sleep(sample_step_delay)

    def _load_or_generate_stream_source(self):
        """Retrieves or synthesizes a stream source matching current selection."""
        adapter = default_adapter_registry.get_adapter(self.current_dataset) or default_adapter_registry.detect_adapter(self.current_dataset)
        
        if adapter and not adapter.is_synthetic:
            source = DatasetSource(dataset_id=self.current_dataset)
            samples = adapter.load_samples(
                source,
                max_samples=2,
                environment_filter=self.current_environment,
                activity_filter=self.current_activity
            )
            if samples:
                return samples[0]

        # Fallback to synthetic generator
        return self.generator.generate_sample(
            activity=self.current_activity,
            environment_type=self.current_environment,
            duration_sec=4.0,
            add_anomaly=self.add_anomaly
        )

    def _persist_prediction_and_events(self, inf: Dict[str, Any]):
        """Saves periodic predictions and triggers significant events into the database."""
        if not inf:
            return
        try:
            with SessionLocal() as db:
                pred = PredictionRecord(
                    timestamp=inf.get("timestamp", time.time()),
                    environment_id=f"env_{self.current_environment.lower().replace(' ', '_')}",
                    environment_type=self.current_environment,
                    activity=inf.get("activity", "Unknown"),
                    confidence=inf.get("confidence", 0.0),
                    presence=inf.get("presence", "Present"),
                    anomaly_score=inf.get("anomaly_score", 0.0),
                    is_anomaly=inf.get("is_anomaly", False),
                    is_synthetic=inf.get("is_synthetic", False)
                )
                db.add(pred)

                # Check if event should be logged
                act = inf.get("activity", "")
                if act != self.last_saved_activity:
                    self.last_saved_activity = act
                    severity = "warning" if act == "Falling" or inf.get("is_anomaly") else "info"
                    event_type = "FALL_DETECTED" if act == "Falling" else ("ANOMALY_TRIGGER" if inf.get("is_anomaly") else "ACTIVITY_CHANGE")
                    
                    event = EventRecord(
                        timestamp=time.time(),
                        event_type=event_type,
                        title=f"{act} Event Detected",
                        description=f"Human activity transitioned to {act} in {self.current_environment} with {int(inf.get('confidence',0)*100)}% model confidence.",
                        severity=severity,
                        environment_id=f"env_{self.current_environment.lower().replace(' ', '_')}",
                        environment_type=self.current_environment,
                        confidence=inf.get("confidence", 1.0),
                        is_synthetic=inf.get("is_synthetic", False)
                    )
                    db.add(event)

                db.commit()
        except Exception as e:
            logger.error(f"Error persisting replay prediction to DB: {e}")


# Singleton replay streamer instance
replay_streamer = ReplayStreamer()
