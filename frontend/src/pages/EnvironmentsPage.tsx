import React, { useState, useEffect } from 'react';
import { Environment, EnvironmentType } from '../types';
import { api } from '../services/api';
import { Modal } from '../components/Modal';
import {
  Building2,
  Plus,
  Compass,
  CheckCircle2,
  AlertCircle,
  Sliders,
  Trash2,
  Sparkles,
  ShieldAlert
} from 'lucide-react';

const ENV_TYPES: EnvironmentType[] = [
  'Office',
  'Classroom',
  'Residential',
  'Healthcare',
  'Industrial',
  'Hospitality',
  'Public Space',
  'Custom',
];

export const EnvironmentsPage: React.FC = () => {
  const [environments, setEnvironments] = useState<Environment[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);
  const [calibratingId, setCalibratingId] = useState<string | null>(null);

  // New Environment form state
  const [newEnv, setNewEnv] = useState({
    id: '',
    name: '',
    type: 'Office' as EnvironmentType,
    description: '',
    multipath_scale: 1.0,
    noise_floor: 0.05,
  });

  const fetchEnvironments = async () => {
    try {
      setLoading(true);
      const data = await api.getEnvironments();
      setEnvironments(data);
    } catch (err) {
      console.error('Failed to load environments:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEnvironments();
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const generatedId = newEnv.id || `env_${newEnv.name.toLowerCase().replace(/\s+/g, '_')}`;
      await api.createEnvironment({
        ...newEnv,
        id: generatedId,
      });
      setIsModalOpen(false);
      setNewEnv({
        id: '',
        name: '',
        type: 'Office',
        description: '',
        multipath_scale: 1.0,
        noise_floor: 0.05,
      });
      fetchEnvironments();
    } catch (err: any) {
      alert(err.message || 'Failed to create environment.');
    }
  };

  const handleCalibrate = async (id: string) => {
    try {
      setCalibratingId(id);
      await api.calibrateEnvironment(id);
      await fetchEnvironments();
    } catch (err: any) {
      alert(err.message || 'Calibration failed');
    } finally {
      setCalibratingId(null);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this environment profile?')) return;
    try {
      await api.deleteEnvironment(id);
      fetchEnvironments();
    } catch (err: any) {
      alert(err.message || 'Failed to delete environment.');
    }
  };

  return (
    <div className="space-y-6">
      {/* Header & Action */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-md">
        <div>
          <h2 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
            <Building2 className="w-5 h-5 text-brand-400" />
            Environment Profiles & Calibration
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Cross-environment management, ambient multipath baselines, and domain-adaptation profiles.
          </p>
        </div>

        <button
          onClick={() => setIsModalOpen(true)}
          className="flex items-center space-x-2 px-4 py-2.5 rounded-xl text-xs font-bold bg-brand-600 hover:bg-brand-500 text-white shadow-md transition-colors"
        >
          <Plus className="w-4 h-4" />
          <span>Add Environment</span>
        </button>
      </div>

      {/* Environments Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {environments.map((env) => {
          const isCalibrating = calibratingId === env.id;
          return (
            <div
              key={env.id}
              className="bg-slate-900 border border-slate-800 hover:border-slate-700 rounded-2xl p-5 shadow-md transition-all flex flex-col justify-between"
            >
              <div>
                <div className="flex items-start justify-between">
                  <div>
                    <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-brand-500/10 text-brand-400 border border-brand-500/20">
                      {env.type}
                    </span>
                    <h3 className="text-lg font-bold text-white mt-2">{env.name}</h3>
                  </div>

                  <span
                    className={`flex items-center gap-1 text-[11px] font-medium px-2 py-0.5 rounded-full ${
                      env.is_calibrated
                        ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                        : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                    }`}
                  >
                    {env.is_calibrated ? (
                      <>
                        <CheckCircle2 className="w-3 h-3" /> Calibrated
                      </>
                    ) : (
                      <>
                        <AlertCircle className="w-3 h-3" /> Uncalibrated
                      </>
                    )}
                  </span>
                </div>

                <p className="text-xs text-slate-400 mt-2 line-clamp-2">
                  {env.description || 'No description provided.'}
                </p>

                {/* Characteristics Metrics */}
                <div className="grid grid-cols-2 gap-2 my-4 bg-slate-950/60 p-3 rounded-xl border border-slate-800/80 text-xs">
                  <div>
                    <span className="text-[11px] text-slate-400">Multipath Scale:</span>
                    <p className="font-mono font-bold text-white mt-0.5">{env.multipath_scale}x</p>
                  </div>
                  <div>
                    <span className="text-[11px] text-slate-400">Noise Floor:</span>
                    <p className="font-mono font-bold text-white mt-0.5">{env.noise_floor}</p>
                  </div>
                </div>
              </div>

              {/* Actions */}
              <div className="flex items-center space-x-2 pt-3 border-t border-slate-800/80">
                <button
                  onClick={() => handleCalibrate(env.id)}
                  disabled={isCalibrating}
                  className={`flex-1 flex items-center justify-center space-x-1.5 py-2 px-3 rounded-xl text-xs font-bold transition-all ${
                    isCalibrating
                      ? 'bg-brand-700 text-white cursor-wait'
                      : 'bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700'
                  }`}
                >
                  <Compass className={`w-3.5 h-3.5 ${isCalibrating ? 'animate-spin' : 'text-brand-400'}`} />
                  <span>{isCalibrating ? 'Calibrating...' : 'Calibrate Baseline'}</span>
                </button>

                <button
                  onClick={() => handleDelete(env.id)}
                  className="p-2 rounded-xl text-slate-400 hover:text-rose-400 hover:bg-rose-950/30 border border-slate-800 transition-colors"
                  title="Delete Environment"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {/* Modal: Create Environment */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title="Create New Environment Profile"
      >
        <form onSubmit={handleCreate} className="space-y-4 text-xs">
          <div>
            <label className="block text-slate-300 font-semibold mb-1">Environment Name</label>
            <input
              type="text"
              required
              placeholder="e.g. Healthcare Patient Room A"
              value={newEnv.name}
              onChange={(e) => setNewEnv({ ...newEnv, name: e.target.value })}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white focus:outline-none focus:border-brand-500"
            />
          </div>

          <div>
            <label className="block text-slate-300 font-semibold mb-1">Environment Type</label>
            <select
              value={newEnv.type}
              onChange={(e) => setNewEnv({ ...newEnv, type: e.target.value as EnvironmentType })}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white focus:outline-none focus:border-brand-500"
            >
              {ENV_TYPES.map((t) => (
                <option key={t} value={t}>
                  {t}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-slate-300 font-semibold mb-1">Description</label>
            <textarea
              rows={3}
              placeholder="Physical dimension, furniture density, through-wall characteristics..."
              value={newEnv.description}
              onChange={(e) => setNewEnv({ ...newEnv, description: e.target.value })}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white focus:outline-none focus:border-brand-500"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-slate-300 font-semibold mb-1">Multipath Scale</label>
              <input
                type="number"
                step="0.1"
                min="0.2"
                max="5.0"
                value={newEnv.multipath_scale}
                onChange={(e) => setNewEnv({ ...newEnv, multipath_scale: parseFloat(e.target.value) })}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white focus:outline-none focus:border-brand-500"
              />
            </div>
            <div>
              <label className="block text-slate-300 font-semibold mb-1">Noise Floor</label>
              <input
                type="number"
                step="0.01"
                min="0.01"
                max="1.0"
                value={newEnv.noise_floor}
                onChange={(e) => setNewEnv({ ...newEnv, noise_floor: parseFloat(e.target.value) })}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white focus:outline-none focus:border-brand-500"
              />
            </div>
          </div>

          <div className="flex justify-end space-x-3 pt-4 border-t border-slate-800">
            <button
              type="button"
              onClick={() => setIsModalOpen(false)}
              className="px-4 py-2 rounded-xl text-slate-400 hover:text-white"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-5 py-2 rounded-xl font-bold bg-brand-600 hover:bg-brand-500 text-white shadow-md"
            >
              Create Environment
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
