import React, { useState, useEffect } from 'react';
import { Experiment, EnvironmentType } from '../types';
import { api } from '../services/api';
import { Modal } from '../components/Modal';
import {
  FlaskConical,
  Play,
  TrendingUp,
  CheckCircle2,
  AlertCircle,
  Clock,
  Sparkles,
  ArrowRight,
  Layers,
  BarChart,
  ShieldCheck,
  Zap,
  Eye
} from 'lucide-react';

const ENVIRONMENTS: EnvironmentType[] = [
  'Office',
  'Classroom',
  'Residential',
  'Healthcare',
  'Industrial',
  'Hospitality',
  'Public Space',
  'Custom',
];

export const ExperimentsPage: React.FC = () => {
  const [experiments, setExperiments] = useState<Experiment[]>([]);
  const [selectedExp, setSelectedExp] = useState<Experiment | null>(null);
  const [isRunning, setIsRunning] = useState<boolean>(false);
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);

  // New Experiment Form State
  const [formState, setFormState] = useState({
    name: '',
    experiment_type: 'cross_environment' as 'same_environment' | 'cross_environment' | 'multi_environment' | 'adaptation',
    dataset_id: 'synthetic_demo_dataset',
    training_environments: ['Office'],
    test_environments: ['Classroom'],
    model_architecture: 'Random Forest',
    random_seed: 42,
    max_samples_per_env: 25,
  });

  const fetchExperiments = async () => {
    try {
      const data = await api.getExperiments();
      setExperiments(data);
    } catch (err) {
      console.error('Error fetching experiments:', err);
    }
  };

  useEffect(() => {
    fetchExperiments();
  }, []);

  const handleRun = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsRunning(true);
    try {
      const res = await api.runExperiment({
        ...formState,
        name: formState.name || `${formState.model_architecture} ${formState.experiment_type.replace('_', ' ').toUpperCase()}`,
      });
      setIsModalOpen(false);
      await fetchExperiments();
      setSelectedExp(res);
    } catch (err: any) {
      alert(`Experiment execution failed: ${err.message}`);
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-md">
        <div>
          <h2 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
            <FlaskConical className="w-5 h-5 text-brand-400" />
            Cross-Environment & Adaptation Experiment Engine
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Evaluate model generalization across rooms, compare baseline transfer vs CORAL domain adaptation.
          </p>
        </div>

        <button
          onClick={() => setIsModalOpen(true)}
          className="flex items-center space-x-2 px-4 py-2.5 rounded-xl text-xs font-bold bg-brand-600 hover:bg-brand-500 text-white shadow-md transition-colors"
        >
          <Play className="w-4 h-4 fill-white" />
          <span>Launch New Experiment</span>
        </button>
      </div>

      {/* Experiments List */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden shadow-md">
        <div className="p-4 border-b border-slate-800 flex items-center justify-between">
          <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400">
            Executed Benchmark Experiments ({experiments.length})
          </h3>
          <span className="text-[11px] font-mono text-emerald-400 flex items-center gap-1">
            <ShieldCheck className="w-3.5 h-3.5" /> Dynamic Un-Fabricated Metrics
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-950 border-b border-slate-800 text-slate-400 font-semibold uppercase tracking-wider">
              <tr>
                <th className="py-3 px-4">Experiment Name</th>
                <th className="py-3 px-4">Type</th>
                <th className="py-3 px-4">Architecture</th>
                <th className="py-3 px-4">Train Envs → Test Envs</th>
                <th className="py-3 px-4 text-center">Accuracy</th>
                <th className="py-3 px-4 text-center">Macro F1</th>
                <th className="py-3 px-4 text-center">Adaptation $\Delta$</th>
                <th className="py-3 px-4 text-right">Details</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/80">
              {experiments.map((exp) => {
                const acc = exp.metrics?.accuracy !== undefined ? (exp.metrics.accuracy * 100).toFixed(1) : '--';
                const f1 = exp.metrics?.f1_macro !== undefined ? (exp.metrics.f1_macro * 100).toFixed(1) : '--';
                const adaptDelta = exp.adaptation_comparison?.accuracy_delta;

                return (
                  <tr key={exp.id} className="hover:bg-slate-850/50 transition-colors">
                    <td className="py-3.5 px-4 font-bold text-white">
                      <div>{exp.name}</div>
                      <div className="text-[10px] text-slate-400 font-mono">{exp.id}</div>
                    </td>

                    <td className="py-3.5 px-4">
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-slate-800 text-brand-300">
                        {exp.experiment_type.replace('_', ' ')}
                      </span>
                    </td>

                    <td className="py-3.5 px-4 font-semibold text-slate-200">
                      {exp.model_architecture}
                    </td>

                    <td className="py-3.5 px-4 text-slate-300">
                      <div className="flex items-center space-x-1.5 font-mono text-[11px]">
                        <span className="text-slate-200">{exp.training_environments.join('+')}</span>
                        <ArrowRight className="w-3 h-3 text-slate-500" />
                        <span className="text-brand-400 font-bold">{exp.test_environments.join('+')}</span>
                      </div>
                    </td>

                    <td className="py-3.5 px-4 text-center font-mono font-bold text-white">
                      {acc}%
                    </td>

                    <td className="py-3.5 px-4 text-center font-mono font-bold text-brand-300">
                      {f1}%
                    </td>

                    <td className="py-3.5 px-4 text-center">
                      {adaptDelta !== undefined ? (
                        <span
                          className={`font-mono text-[11px] font-bold px-2 py-0.5 rounded ${
                            adaptDelta >= 0
                              ? 'bg-emerald-500/20 text-emerald-400'
                              : 'bg-rose-500/20 text-rose-400'
                          }`}
                        >
                          {adaptDelta >= 0 ? `+${(adaptDelta * 100).toFixed(1)}%` : `${(adaptDelta * 100).toFixed(1)}%`}
                        </span>
                      ) : (
                        <span className="text-slate-600 font-mono">N/A</span>
                      )}
                    </td>

                    <td className="py-3.5 px-4 text-right">
                      <button
                        onClick={() => setSelectedExp(exp)}
                        className="px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 inline-flex items-center gap-1 transition-colors"
                      >
                        <Eye className="w-3.5 h-3.5 text-brand-400" />
                        <span>View</span>
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Modal: Launch New Experiment */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title="Configure & Launch AI Experiment"
      >
        <form onSubmit={handleRun} className="space-y-4 text-xs">
          <div>
            <label className="block text-slate-300 font-semibold mb-1">Experiment Title</label>
            <input
              type="text"
              placeholder="e.g. Cross-Room Generalization (Office -> Healthcare)"
              value={formState.name}
              onChange={(e) => setFormState({ ...formState, name: e.target.value })}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white focus:outline-none focus:border-brand-500"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-slate-300 font-semibold mb-1">Experiment Type</label>
              <select
                value={formState.experiment_type}
                onChange={(e) =>
                  setFormState({
                    ...formState,
                    experiment_type: e.target.value as any,
                  })
                }
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white focus:outline-none focus:border-brand-500"
              >
                <option value="same_environment">Same Environment (Train A → Test A)</option>
                <option value="cross_environment">Cross Environment (Train A → Test B)</option>
                <option value="multi_environment">Multi Environment (Train A+B → Test C)</option>
                <option value="adaptation">Adaptation Benchmark (Baseline vs Adapted)</option>
              </select>
            </div>

            <div>
              <label className="block text-slate-300 font-semibold mb-1">Model Architecture</label>
              <select
                value={formState.model_architecture}
                onChange={(e) => setFormState({ ...formState, model_architecture: e.target.value })}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white focus:outline-none focus:border-brand-500"
              >
                <option value="Random Forest">Random Forest</option>
                <option value="SVM">Support Vector Machine (SVM)</option>
                <option value="1D CNN">1D Convolutional Neural Network</option>
                <option value="CNN-GRU">CNN-GRU Sequential Recurrent</option>
                <option value="Transformer">Transformer Self-Attention</option>
              </select>
            </div>
          </div>

          {/* Environment Pickers */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-slate-300 font-semibold mb-1">Training Environment(s)</label>
              <select
                multiple
                value={formState.training_environments}
                onChange={(e) => {
                  const opts = Array.from(e.target.selectedOptions, (opt) => opt.value);
                  setFormState({ ...formState, training_environments: opts });
                }}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white focus:outline-none focus:border-brand-500 h-24"
              >
                {ENVIRONMENTS.map((env) => (
                  <option key={env} value={env}>
                    {env}
                  </option>
                ))}
              </select>
              <span className="text-[10px] text-slate-500">Hold Ctrl/Cmd to multi-select</span>
            </div>

            <div>
              <label className="block text-slate-300 font-semibold mb-1">Test Environment(s)</label>
              <select
                multiple
                value={formState.test_environments}
                onChange={(e) => {
                  const opts = Array.from(e.target.selectedOptions, (opt) => opt.value);
                  setFormState({ ...formState, test_environments: opts });
                }}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white focus:outline-none focus:border-brand-500 h-24"
              >
                {ENVIRONMENTS.map((env) => (
                  <option key={env} value={env}>
                    {env}
                  </option>
                ))}
              </select>
              <span className="text-[10px] text-slate-500">Hold Ctrl/Cmd to multi-select</span>
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
              disabled={isRunning}
              className="px-5 py-2 rounded-xl font-bold bg-brand-600 hover:bg-brand-500 text-white shadow-md disabled:opacity-50 flex items-center gap-1.5"
            >
              {isRunning && <Clock className="w-3.5 h-3.5 animate-spin" />}
              <span>{isRunning ? 'Running Experiment...' : 'Execute Experiment'}</span>
            </button>
          </div>
        </form>
      </Modal>

      {/* Modal: Experiment Details */}
      <Modal
        isOpen={!!selectedExp}
        onClose={() => setSelectedExp(null)}
        title={`Experiment Results: ${selectedExp?.name || ''}`}
        maxWidth="max-w-3xl"
      >
        {selectedExp && (
          <div className="space-y-5 text-xs">
            {/* Primary Metrics Grid */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 bg-slate-950 p-4 rounded-xl border border-slate-800 text-center">
              <div>
                <span className="text-[11px] text-slate-400">Accuracy</span>
                <p className="text-2xl font-black text-white">
                  {((selectedExp.metrics?.accuracy || 0) * 100).toFixed(2)}%
                </p>
              </div>
              <div>
                <span className="text-[11px] text-slate-400">Macro F1</span>
                <p className="text-2xl font-black text-white">
                  {((selectedExp.metrics?.f1_macro || 0) * 100).toFixed(2)}%
                </p>
              </div>
              <div>
                <span className="text-[11px] text-slate-400">Train Samples</span>
                <p className="text-2xl font-black text-white">{selectedExp.training_samples_count}</p>
              </div>
              <div>
                <span className="text-[11px] text-slate-400">Test Samples</span>
                <p className="text-2xl font-black text-white">{selectedExp.test_samples_count}</p>
              </div>
            </div>

            {/* Adaptation Benchmark Comparison if Available */}
            {selectedExp.adaptation_comparison && (
              <div className="bg-slate-950 p-4 rounded-xl border border-slate-800">
                <h4 className="text-xs font-bold text-white uppercase tracking-wider mb-3 flex items-center gap-1.5">
                  <Zap className="w-4 h-4 text-accent-amber" />
                  Baseline vs Environment-Adapted Model Comparison
                </h4>
                <div className="grid grid-cols-2 gap-4 text-center">
                  <div className="p-3 rounded-lg bg-slate-900 border border-slate-800">
                    <span className="text-[11px] text-slate-400">Baseline (No Adaptation)</span>
                    <p className="text-lg font-bold text-slate-300 mt-1">
                      {((selectedExp.adaptation_comparison.baseline_metrics.accuracy || 0) * 100).toFixed(1)}% Acc /{' '}
                      {((selectedExp.adaptation_comparison.baseline_metrics.f1_macro || 0) * 100).toFixed(1)}% F1
                    </p>
                  </div>
                  <div className="p-3 rounded-lg bg-brand-950/40 border border-brand-800/60">
                    <span className="text-[11px] text-brand-300">Adapted (CORAL Alignment)</span>
                    <p className="text-lg font-black text-brand-400 mt-1">
                      {((selectedExp.adaptation_comparison.adapted_metrics.accuracy || 0) * 100).toFixed(1)}% Acc /{' '}
                      {((selectedExp.adaptation_comparison.adapted_metrics.f1_macro || 0) * 100).toFixed(1)}% F1
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* Confusion Matrix */}
            {selectedExp.metrics?.confusion_matrix && selectedExp.metrics?.labels && (
              <div>
                <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-2">
                  Test Confusion Matrix
                </h4>
                <div className="overflow-x-auto bg-slate-950 p-4 rounded-xl border border-slate-800">
                  <table className="w-full text-center font-mono text-[11px]">
                    <thead>
                      <tr>
                        <th className="p-1 text-slate-500 text-left">True \ Pred</th>
                        {selectedExp.metrics.labels.map((lbl, idx) => (
                          <th key={idx} className="p-1 text-brand-400 truncate max-w-[80px]">
                            {lbl}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {selectedExp.metrics.confusion_matrix.map((row, rIdx) => (
                        <tr key={rIdx}>
                          <td className="p-1 font-semibold text-slate-300 text-left">
                            {selectedExp.metrics.labels?.[rIdx]}
                          </td>
                          {row.map((val, cIdx) => (
                            <td
                              key={cIdx}
                              className={`p-1.5 rounded ${
                                rIdx === cIdx
                                  ? val > 0
                                    ? 'bg-emerald-500/20 text-emerald-300 font-bold'
                                    : 'text-slate-500'
                                  : val > 0
                                  ? 'bg-rose-500/20 text-rose-300 font-bold'
                                  : 'text-slate-600'
                              }`}
                            >
                              {val}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        )}
      </Modal>
    </div>
  );
};
