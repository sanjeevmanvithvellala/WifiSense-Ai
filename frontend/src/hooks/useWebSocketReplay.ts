import { useState, useEffect, useRef, useCallback } from 'react';
import { ReplayFrame } from '../types';

export function useWebSocketReplay() {
  const [isConnected, setIsConnected] = useState<boolean>(false);
  const [lastFrame, setLastFrame] = useState<ReplayFrame | null>(null);
  const [history, setHistory] = useState<ReplayFrame[]>([]);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<any>(null);

  const connect = useCallback(() => {
    // Robust connection URL resolution: port 5173 / 3000 -> connects to FastAPI on port 8000
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    let wsHost = window.location.host;
    if (window.location.port === '5173' || window.location.port === '3000') {
      wsHost = `${window.location.hostname}:8000`;
    }
    const wsUrl = `${protocol}//${wsHost}/ws/replay`;

    try {
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        wsRef.current.close();
      }

      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        setIsConnected(true);
        console.log('[WebSocket] Connected to WiFiSense AI live stream at', wsUrl);
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          const frameData: ReplayFrame = {
            type: data.type || 'CSI_REPLAY_FRAME',
            timestamp: data.timestamp || Date.now() / 1000,
            environment: data.environment || data.environment_id || 'Office',
            dataset_id: data.dataset_id || 'live_stream',
            is_synthetic: data.is_synthetic !== undefined ? data.is_synthetic : true,
            is_replay: data.is_replay !== undefined ? data.is_replay : true,
            source_mode: data.source_mode || data.source || 'LIVE STREAM',
            subcarrier_count: data.subcarrier_count || (data.frame_amplitude ? data.frame_amplitude.length : (data.waveform_preview ? data.waveform_preview.length : 64)),
            frame_amplitude: data.frame_amplitude || data.waveform_preview || [],
            heatmap_matrix: data.heatmap_matrix || [],
            inference: data.inference || {
              activity: data.activity || 'Walking',
              confidence: data.confidence || 0.9,
              class_probabilities: data.probabilities || {},
              presence: data.presence ? 'Present' : 'Absent',
              presence_confidence: data.presence_score || 0.95,
              anomaly_score: data.anomaly_score || 0.05,
              is_anomaly: data.is_anomaly || false,
              is_synthetic: data.is_synthetic !== undefined ? data.is_synthetic : true,
              environment_type: data.environment || 'Office',
            }
          };

          setLastFrame(frameData);
          setHistory((prev) => {
            const updated = [...prev, frameData];
            return updated.length > 50 ? updated.slice(updated.length - 50) : updated;
          });
        } catch (err) {
          console.error('[WebSocket] Error parsing frame payload:', err);
        }
      };

      ws.onerror = (err) => {
        console.warn('[WebSocket] Connection error:', err);
      };

      ws.onclose = () => {
        setIsConnected(false);
        console.log('[WebSocket] Connection closed. Retrying in 2.5s...');
        reconnectTimeoutRef.current = setTimeout(connect, 2500);
      };
    } catch (err) {
      console.error('[WebSocket] Failed to initialize socket:', err);
      reconnectTimeoutRef.current = setTimeout(connect, 3000);
    }
  }, []);

  useEffect(() => {
    connect();
    return () => {
      if (reconnectTimeoutRef.current) clearTimeout(reconnectTimeoutRef.current);
      if (wsRef.current) wsRef.current.close();
    };
  }, [connect]);

  return {
    isConnected,
    lastFrame,
    history,
    reconnect: connect,
  };
}
