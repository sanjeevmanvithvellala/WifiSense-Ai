import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import {
  Settings,
  Save,
  Shield,
  Sliders,
  CheckCircle2,
  Cpu,
  Radio,
  Building2,
  Lock
} from 'lucide-react';

export const SettingsPage: React.FC = () => {
  const [settings, setSettings] = useState<Record<string, any>>({
    default_environment: 'Office',
    default_dataset: 'synthetic_demo_dataset',
    default_model: 'model_random_forest_demo',
    replay_playback_speed: 1.0,
    anomaly_threshold: 0.5,
    privacy_mode: true,
    butterworth_cutoff_hz: 12.0,
    hampel_window: 5,
  });
  const [isSaved, setIsSaved] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    api.getSettings()
      .then((data) => {
        const parsed: Record<string, any> = {};
        for (const [k, v] of Object.entries(data)) {
          parsed[k] = v.value;
        }
        setSettings((prev) => ({ ...prev, ...parsed }));
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.updateSettings(settings);
      setIsSaved(true);
      setTimeout(() => setIsSaved(false), 3000);
    } catch (err: any) {
      alert(`Failed to save settings: ${err.message}`);
    }
  };

  return (
    <div className="space-y-6 max-w-4xl">
      {/* Top Banner */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-md">
        <h2 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
          <Settings className="w-5 h-5 text-brand-400" />
          System Settings & Signal Pipeline Configuration
        </h2>
        <p className="text-xs text-slate-400 mt-0.5">
          Configure default inference environments, signal preprocessing filters, and privacy safety parameters.
        </p>
      </div>

      <form onSubmit={handleSave} className="space-y-6 text-xs">
        {/* 1. Privacy & Safety Settings */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-md">
          <h3 className="text-xs font-bold uppercase tracking-wider text-white mb-4 flex items-center gap-2">
            <Shield className="w-4 h-4 text-emerald-400" />
            Privacy & Ethical Safety Configuration
          </h3>

          <div className="space-y-4">
            <div className="flex items-center justify-between p-3.5 rounded-xl bg-slate-950/60 border border-slate-800/80">
              <div>
                <h4 className="font-bold text-white">Privacy Preservation Mode</h4>
                <p className="text-[11px] text-slate-400 mt-0.5">
                  Ensures only numerical radio multipath signal features are processed. Disallows any biometric profiling, person identification, or facial tracking.
                </p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={settings.privacy_mode}
                  onChange={(e) => setSettings({ ...settings, privacy_mode: e.target.checked })}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-slate-800 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-emerald-600"></div>
              </label>
            </div>
          </div>
        </div>

        {/* 2. Pipeline Hyperparameters */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-md">
          <h3 className="text-xs font-bold uppercase tracking-wider text-white mb-4 flex items-center gap-2">
            <Sliders className="w-4 h-4 text-brand-400" />
            Signal Conditioning & Anomaly Sensitivity
          </h3>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block font-semibold text-slate-300 mb-1">
                Anomaly Detection Sensitivity Threshold ({settings.anomaly_threshold})
              </label>
              <input
                type="range"
                min="0.1"
                max="0.9"
                step="0.05"
                value={settings.anomaly_threshold}
                onChange={(e) => setSettings({ ...settings, anomaly_threshold: parseFloat(e.target.value) })}
                className="w-full accent-brand-500"
              />
              <span className="text-[10px] text-slate-500">Lower values make anomaly triggers more sensitive</span>
            </div>

            <div>
              <label className="block font-semibold text-slate-300 mb-1">
                Butterworth Low-pass Filter Cutoff ({settings.butterworth_cutoff_hz || 12.0} Hz)
              </label>
              <input
                type="range"
                min="4.0"
                max="24.0"
                step="1.0"
                value={settings.butterworth_cutoff_hz || 12.0}
                onChange={(e) => setSettings({ ...settings, butterworth_cutoff_hz: parseFloat(e.target.value) })}
                className="w-full accent-brand-500"
              />
              <span className="text-[10px] text-slate-500">Filters high-frequency burst and RF thermal noise</span>
            </div>
          </div>
        </div>

        {/* Save Bar */}
        <div className="flex items-center justify-between p-4 bg-slate-900 border border-slate-800 rounded-2xl shadow-md">
          <span className="text-xs text-slate-400 font-medium">
            Changes will take effect across active WebSocket stream and ML pipeline.
          </span>

          <div className="flex items-center space-x-3">
            {isSaved && (
              <span className="text-emerald-400 font-bold flex items-center gap-1">
                <CheckCircle2 className="w-4 h-4" /> Saved Successfully!
              </span>
            )}

            <button
              type="submit"
              className="flex items-center space-x-2 px-6 py-2.5 rounded-xl font-bold bg-brand-600 hover:bg-brand-500 text-white shadow-md transition-colors"
            >
              <Save className="w-4 h-4" />
              <span>Save Settings</span>
            </button>
          </div>
        </div>
      </form>
    </div>
  );
};
