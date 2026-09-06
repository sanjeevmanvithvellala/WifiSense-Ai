import React, { useState, useEffect } from 'react';
import { ActivityCard } from '../components/ActivityCard';
import { SignalWaveform } from '../components/SignalWaveform';
import { HeatmapVisualization } from '../components/HeatmapVisualization';
import { SpatialPresenceHeatmap } from '../components/SpatialPresenceHeatmap';
import { SystemStatusBadge } from '../components/SystemStatusBadge';
import { ReplayFrame, HealthStatus, EventLog } from '../types';
import { api } from '../services/api';
import { Play, Pause, AlertCircle, Clock, ShieldCheck, Radio, ArrowRight } from 'lucide-react';

interface DashboardPageProps {
  lastFrame: ReplayFrame | null;
  health: HealthStatus | null;
  onNavigateToLive: () => void;
}

export const DashboardPage: React.FC<DashboardPageProps> = ({
  lastFrame,
  health,
  onNavigateToLive,
}) => {
  const [events, setEvents] = useState<EventLog[]>([]);
  const [isPlaying, setIsPlaying] = useState<boolean>(true);

  const fetchEvents = async () => {
    try {
      const data = await api.getEvents(8);
      setEvents(data);
    } catch (_) {}
  };

  useEffect(() => {
    fetchEvents();
    const interval = setInterval(fetchEvents, 4000);
    return () => clearInterval(interval);
  }, []);

  const inference = lastFrame?.inference || {
    activity: 'Walking',
    confidence: 0.94,
    presence: 'Present',
    presence_confidence: 0.98,
    anomaly_score: 0.08,
    is_anomaly: false,
    environment_type: 'Office',
    dynamic_energy: 0.52,
    is_synthetic: true,
  };

  const handleTogglePlay = async () => {
    try {
      const nextAction = isPlaying ? 'pause' : 'resume';
      await api.controlReplay({ action: nextAction });
      setIsPlaying(!isPlaying);
    } catch (err) {
      console.error('Error toggling replay:', err);
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Banner with Quick Controls */}
      <div className="bg-gradient-to-r from-slate-900 via-slate-850 to-slate-900 border border-slate-800 rounded-2xl p-5 flex flex-col md:flex-row md:items-center md:justify-between gap-4 shadow-lg">
        <div>
          <div className="flex items-center space-x-2">
            <span className="px-2 py-0.5 rounded text-[11px] font-bold uppercase tracking-wider bg-brand-500/20 text-brand-300 border border-brand-500/30">
              Live Intelligence
            </span>
            <span className="text-xs text-slate-400">
              Active Stream: <strong className="text-slate-200">{lastFrame?.dataset_id || 'Synthetic Demo Dataset'}</strong>
            </span>
          </div>
          <h2 className="text-xl font-extrabold text-white tracking-tight mt-1">
            Real-Time Human Activity Sensing Overview
          </h2>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={handleTogglePlay}
            className={`flex items-center space-x-2 px-4 py-2 rounded-xl text-xs font-bold transition-all shadow-md ${
              isPlaying
                ? 'bg-amber-600 hover:bg-amber-500 text-white'
                : 'bg-brand-600 hover:bg-brand-500 text-white'
            }`}
          >
            {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
            <span>{isPlaying ? 'Pause Feed' : 'Resume Feed'}</span>
          </button>

          <button
            onClick={onNavigateToLive}
            className="flex items-center space-x-2 px-4 py-2 rounded-xl text-xs font-bold bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition-colors"
          >
            <Radio className="w-4 h-4 text-brand-400" />
            <span>Open Live Replay UI</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* 1. Core HAR, Presence, Anomaly Cards */}
      <ActivityCard
        activity={inference.activity}
        confidence={inference.confidence}
        presence={inference.presence}
        presenceConfidence={inference.presence_confidence}
        anomalyScore={inference.anomaly_score}
        isAnomaly={inference.is_anomaly}
        dynamicEnergy={inference.dynamic_energy}
        isSynthetic={inference.is_synthetic}
      />

      {/* 2. Real-Time Spatial Room Radar & Physical Presence Heatmap */}
      <SpatialPresenceHeatmap
        activity={inference.activity}
        confidence={inference.confidence}
        presence={inference.presence}
        isAnomaly={inference.is_anomaly}
        anomalyScore={inference.anomaly_score}
        subcarrierAmplitudes={lastFrame?.frame_amplitude || []}
        environmentType={inference.environment_type}
        sourceMode={inference.is_synthetic ? 'Simulated CSI' : 'Live Stream'}
        height={260}
      />

      {/* 3. Real-Time CSI Signal Waveform & Spectrogram Heatmap */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <SignalWaveform
          amplitudes={lastFrame?.frame_amplitude || []}
          title="Current CSI Frame Subcarrier Profile"
          height={190}
        />
        <HeatmapVisualization
          matrix={lastFrame?.heatmap_matrix || []}
          title="Temporal Spectrogram Doppler Heatmap"
          height={190}
        />
      </div>

      {/* 3. Event Log and Subsystem Status */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Events List */}
        <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-md flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-2">
                <Clock className="w-4 h-4 text-brand-400" />
                Recent Intelligence Event Log
              </h3>
              <span className="text-[11px] text-slate-400 font-mono">Real-time telemetry</span>
            </div>

            <div className="space-y-2.5">
              {events.length === 0 ? (
                <div className="text-center py-8 text-slate-500 text-xs">
                  Awaiting activity transition events...
                </div>
              ) : (
                events.map((ev) => (
                  <div
                    key={ev.id}
                    className="p-3 rounded-xl bg-slate-950/60 border border-slate-800/80 flex items-start justify-between gap-3 text-xs"
                  >
                    <div className="flex items-start space-x-2.5">
                      <span
                        className={`w-2 h-2 rounded-full mt-1.5 shrink-0 ${
                          ev.severity === 'critical'
                            ? 'bg-rose-500'
                            : ev.severity === 'warning'
                            ? 'bg-amber-500'
                            : 'bg-brand-400'
                        }`}
                      ></span>
                      <div>
                        <div className="flex items-center gap-2">
                          <h4 className="font-bold text-white">{ev.title}</h4>
                          <span className="px-1.5 py-0.2 rounded bg-slate-800 text-[10px] text-slate-400">
                            {ev.environment_type}
                          </span>
                        </div>
                        <p className="text-slate-400 mt-0.5 leading-relaxed">{ev.description}</p>
                      </div>
                    </div>
                    <span className="font-mono text-[10px] text-slate-400 shrink-0">
                      {new Date(ev.timestamp * 1000).toLocaleTimeString()}
                    </span>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

        {/* Subsystem Health Status Card */}
        <div className="flex flex-col justify-between">
          <SystemStatusBadge health={health} />
        </div>
      </div>
    </div>
  );
};
