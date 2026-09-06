import React, { useState, useEffect } from 'react';
import { SignalWaveform } from '../components/SignalWaveform';
import { HeatmapVisualization } from '../components/HeatmapVisualization';
import { SpatialPresenceHeatmap } from '../components/SpatialPresenceHeatmap';
import { ActivityCard } from '../components/ActivityCard';
import { ReplayFrame, Dataset, Environment, MLModel } from '../types';
import { api } from '../services/api';
import {
  Play,
  Pause,
  RotateCcw,
  Square,
  Radio,
  Sliders,
  Sparkles,
  AlertTriangle,
  Layers,
  Building2,
  Cpu
} from 'lucide-react';

interface LiveAnalysisPageProps {
  lastFrame: ReplayFrame | null;
}

const SCENARIOS = [
  { id: 'Walking', label: 'Office Walking', desc: '1.8Hz periodic Doppler stride signature' },
  { id: 'Sitting', label: 'Classroom Sitting', desc: 'Subtle torso micromotion & steady baseline' },
  { id: 'Standing', label: 'Standing Breathing', desc: '0.22Hz thoracic cavity expansion' },
  { id: 'Running', label: 'High-Speed Running', desc: 'Wideband high-energy Doppler dispersion' },
  { id: 'Falling', label: 'Healthcare Fall', desc: 'Sharp transient shock impact followed by cessation' },
  { id: 'Waving', label: 'Hand Waving Gesture', desc: 'Localized subcarrier modulation ~2.1Hz' },
  { id: 'Empty', label: 'Empty Room (Absent)', desc: 'Static multipath reflections only (Presence: Absent)' },
];

export const LiveAnalysisPage: React.FC<LiveAnalysisPageProps> = ({ lastFrame }) => {
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [environments, setEnvironments] = useState<Environment[]>([]);
  const [models, setModels] = useState<MLModel[]>([]);
  
  const [selectedDataset, setSelectedDataset] = useState<string>('synthetic_demo_dataset');
  const [selectedEnvironment, setSelectedEnvironment] = useState<string>('Office');
  const [selectedScenario, setSelectedScenario] = useState<string>('Walking');
  const [selectedModel, setSelectedModel] = useState<string>('');
  const [sourceMode, setSourceMode] = useState<'synthetic' | 'pc_wifi' | 'hardware_udp'>('synthetic');
  const [playbackSpeed, setPlaybackSpeed] = useState<number>(1.0);
  const [injectAnomaly, setInjectAnomaly] = useState<boolean>(false);
  const [isPlaying, setIsPlaying] = useState<boolean>(true);

  useEffect(() => {
    // Load datasets, environments, models
    api.getDatasets().then(setDatasets).catch(() => {});
    api.getEnvironments().then(setEnvironments).catch(() => {});
    api.getModels().then((m) => {
      setModels(m);
      if (m.length > 0) setSelectedModel(m[0].id);
    }).catch(() => {});
  }, []);

  const handleStartReplay = async (
    scenario = selectedScenario,
    env = selectedEnvironment,
    ds = selectedDataset,
    anomaly = injectAnomaly,
    mode = sourceMode
  ) => {
    try {
      await api.controlReplay({
        action: 'play',
        source_mode: mode,
        dataset_id: ds,
        environment_type: env,
        activity_scenario: scenario,
        playback_speed: playbackSpeed,
        add_anomaly: anomaly,
      });
      setIsPlaying(true);
    } catch (err) {
      console.error('Error starting replay:', err);
    }
  };

  const handlePause = async () => {
    await api.controlReplay({ action: 'pause' });
    setIsPlaying(false);
  };

  const handleStop = async () => {
    await api.controlReplay({ action: 'stop' });
    setIsPlaying(false);
  };

  const handleReset = async () => {
    await api.controlReplay({ action: 'reset' });
    handleStartReplay();
  };

  const inference = lastFrame?.inference || {
    activity: selectedScenario,
    confidence: 0.94,
    presence: selectedScenario.toLowerCase() === 'empty' ? 'Absent' : 'Present',
    presence_confidence: 0.98,
    anomaly_score: injectAnomaly ? 0.85 : 0.08,
    is_anomaly: injectAnomaly || selectedScenario === 'Falling',
    environment_type: selectedEnvironment,
    dynamic_energy: 0.48,
    is_synthetic: true,
  };

  const classProbs = inference.class_probabilities || {
    Walking: 0.88,
    Sitting: 0.04,
    Standing: 0.03,
    Running: 0.02,
    Falling: 0.01,
    Waving: 0.01,
    Empty: 0.01,
  };

  return (
    <div className="space-y-6">
      {/* Explicit Mode Declaration Header Banner */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-lg flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-widest border animate-pulse ${
              sourceMode === 'pc_wifi' 
                ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40' 
                : sourceMode === 'hardware_udp'
                ? 'bg-cyan-500/20 text-cyan-300 border-cyan-500/40'
                : 'bg-amber-500/20 text-amber-300 border-amber-500/40'
            }`}>
              {sourceMode === 'pc_wifi' ? 'LIVE HOME WI-FI FEED' : sourceMode === 'hardware_udp' ? 'HARDWARE UDP STREAM (PORT 5555)' : 'RECORDED CSI REPLAY'}
            </span>
            <span className="text-xs text-slate-400 font-medium">
              {sourceMode === 'pc_wifi' ? 'Real-time Link Physical RSSI Modulation' : sourceMode === 'hardware_udp' ? 'External ESP32 / Broadcom Hardware Feed' : 'Software-Only Simulation & Benchmark Mode'}
            </span>
          </div>
          <h2 className="text-xl font-extrabold text-white tracking-tight mt-1 flex items-center gap-2">
            <Radio className="w-5 h-5 text-brand-400" />
            Live CSI Telemetry & Signal Intelligence Studio
          </h2>
        </div>

        {/* Source Mode Switcher & Playback Controls */}
        <div className="flex flex-wrap items-center gap-2">
          <div className="flex bg-slate-950 p-1 rounded-xl border border-slate-800 text-xs">
            <button
              onClick={() => {
                setSourceMode('synthetic');
                handleStartReplay(selectedScenario, selectedEnvironment, selectedDataset, injectAnomaly, 'synthetic');
              }}
              className={`px-3 py-1.5 rounded-lg font-semibold transition-all ${
                sourceMode === 'synthetic' ? 'bg-brand-600 text-white shadow-sm' : 'text-slate-400 hover:text-white'
              }`}
            >
              Simulated CSI
            </button>
            <button
              onClick={() => {
                setSourceMode('pc_wifi');
                handleStartReplay(selectedScenario, selectedEnvironment, selectedDataset, injectAnomaly, 'pc_wifi');
              }}
              className={`px-3 py-1.5 rounded-lg font-semibold transition-all ${
                sourceMode === 'pc_wifi' ? 'bg-emerald-600 text-white shadow-sm' : 'text-slate-400 hover:text-white'
              }`}
            >
              📶 Live Home Wi-Fi
            </button>
            <button
              onClick={() => {
                setSourceMode('hardware_udp');
                handleStartReplay(selectedScenario, selectedEnvironment, selectedDataset, injectAnomaly, 'hardware_udp');
              }}
              className={`px-3 py-1.5 rounded-lg font-semibold transition-all ${
                sourceMode === 'hardware_udp' ? 'bg-cyan-600 text-white shadow-sm' : 'text-slate-400 hover:text-white'
              }`}
            >
              ⚡ ESP32 UDP
            </button>
          </div>

          <div className="flex items-center space-x-2 bg-slate-950 p-1.5 rounded-xl border border-slate-800">
            <button
              onClick={() => (isPlaying ? handlePause() : handleStartReplay())}
              className={`p-2 rounded-lg font-bold text-white transition-all ${
                isPlaying ? 'bg-amber-600 hover:bg-amber-500' : 'bg-brand-600 hover:bg-brand-500 shadow-md shadow-brand-500/20'
              }`}
              title={isPlaying ? 'Pause' : 'Play'}
            >
              {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
            </button>

            <button
              onClick={handleStop}
              className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition-colors"
              title="Stop"
            >
              <Square className="w-4 h-4" />
            </button>

            <button
              onClick={handleReset}
              className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition-colors"
              title="Reset Buffer"
            >
              <RotateCcw className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Replay Configuration Panel */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-md">
        <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-4 flex items-center gap-2">
          <Sliders className="w-4 h-4 text-brand-400" />
          Replay Source & Scenario Configuration
        </h3>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Dataset Selector */}
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1.5 flex items-center gap-1.5">
              <Layers className="w-3.5 h-3.5 text-slate-400" />
              Source Dataset
            </label>
            <select
              value={selectedDataset}
              onChange={(e) => {
                setSelectedDataset(e.target.value);
                handleStartReplay(selectedScenario, selectedEnvironment, e.target.value);
              }}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-brand-500"
            >
              {datasets.map((d) => (
                <option key={d.id} value={d.id}>
                  {d.name} {d.is_synthetic ? '(Synthetic Demo)' : '(Real Registered)'}
                </option>
              ))}
            </select>
          </div>

          {/* Environment Selector */}
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1.5 flex items-center gap-1.5">
              <Building2 className="w-3.5 h-3.5 text-slate-400" />
              Environment Profile
            </label>
            <select
              value={selectedEnvironment}
              onChange={(e) => {
                setSelectedEnvironment(e.target.value);
                handleStartReplay(selectedScenario, e.target.value, selectedDataset);
              }}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-brand-500"
            >
              {environments.map((env) => (
                <option key={env.id} value={env.type}>
                  {env.name} ({env.type})
                </option>
              ))}
            </select>
          </div>

          {/* Activity Scenario Selector */}
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1.5 flex items-center gap-1.5">
              <Sparkles className="w-3.5 h-3.5 text-slate-400" />
              Movement Scenario
            </label>
            <select
              value={selectedScenario}
              onChange={(e) => {
                setSelectedScenario(e.target.value);
                handleStartReplay(e.target.value, selectedEnvironment, selectedDataset);
              }}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-brand-500"
            >
              {SCENARIOS.map((sc) => (
                <option key={sc.id} value={sc.id}>
                  {sc.label}
                </option>
              ))}
            </select>
          </div>

          {/* Playback Speed & Anomaly Injection */}
          <div className="flex items-center space-x-3">
            <div className="flex-1">
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                Speed ({playbackSpeed}x)
              </label>
              <input
                type="range"
                min="0.5"
                max="3.0"
                step="0.5"
                value={playbackSpeed}
                onChange={(e) => {
                  const spd = parseFloat(e.target.value);
                  setPlaybackSpeed(spd);
                  api.controlReplay({ action: 'play', playback_speed: spd });
                }}
                className="w-full accent-brand-500"
              />
            </div>

            <div className="pt-4">
              <button
                onClick={() => {
                  const next = !injectAnomaly;
                  setInjectAnomaly(next);
                  handleStartReplay(selectedScenario, selectedEnvironment, selectedDataset, next);
                }}
                className={`px-3 py-2 rounded-xl text-xs font-bold border transition-colors flex items-center gap-1.5 ${
                  injectAnomaly
                    ? 'bg-amber-500/20 text-amber-300 border-amber-500/40'
                    : 'bg-slate-800 text-slate-400 border-slate-700 hover:text-slate-200'
                }`}
              >
                <AlertTriangle className="w-3.5 h-3.5" />
                <span>{injectAnomaly ? 'Anomaly ON' : 'Inject Anomaly'}</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Activity Status Cards */}
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

      {/* 2D Spatial Multipath & Human Presence Kinetic Radar Heatmap */}
      <SpatialPresenceHeatmap
        activity={inference.activity}
        confidence={inference.confidence}
        presence={inference.presence}
        isAnomaly={inference.is_anomaly}
        anomalyScore={inference.anomaly_score}
        subcarrierAmplitudes={lastFrame?.frame_amplitude || []}
        environmentType={selectedEnvironment}
        sourceMode={sourceMode}
        height={340}
      />

      {/* Signal Visualizations */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <SignalWaveform
          amplitudes={lastFrame?.frame_amplitude || []}
          title="Streaming CSI Amplitude Waveform"
          height={200}
        />
        <HeatmapVisualization
          matrix={lastFrame?.heatmap_matrix || []}
          title="Streaming Spectrogram Heatmap"
          height={200}
        />
      </div>

      {/* Model Probability Distribution */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-md">
        <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-4 flex items-center justify-between">
          <span className="flex items-center gap-2">
            <Cpu className="w-4 h-4 text-brand-400" />
            Class Probability Distribution Output
          </span>
          <span className="text-[11px] font-mono text-slate-400">Softmax Confidence</span>
        </h3>

        <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-3">
          {Object.entries(classProbs).map(([actName, prob]) => {
            const isTop = actName.toLowerCase() === inference.activity.toLowerCase();
            return (
              <div
                key={actName}
                className={`p-3 rounded-xl border text-center transition-all ${
                  isTop
                    ? 'bg-brand-500/15 border-brand-500/40 shadow-sm'
                    : 'bg-slate-950/60 border-slate-800/80'
                }`}
              >
                <p className="text-[11px] font-semibold text-slate-300 truncate">{actName}</p>
                <p className="text-base font-black text-white mt-1">{Math.round((prob as number) * 100)}%</p>
                <div className="w-full bg-slate-800 rounded-full h-1 mt-2 overflow-hidden">
                  <div
                    className={`h-full rounded-full ${isTop ? 'bg-brand-400' : 'bg-slate-600'}`}
                    style={{ width: `${Math.min(100, Math.max(3, (prob as number) * 100))}%` }}
                  ></div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
