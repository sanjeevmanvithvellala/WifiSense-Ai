import React, { useState, useEffect } from 'react';
import { MLModel } from '../types';
import { api } from '../services/api';
import { Modal } from '../components/Modal';
import {
  Cpu,
  CheckCircle2,
  Sliders,
  Play,
  TrendingUp,
  Clock,
  Sparkles,
  Layers,
  BarChart,
  Eye
} from 'lucide-react';

export const ModelsPage: React.FC = () => {
  const [models, setModels] = useState<MLModel[]>([]);
  const [selectedModel, setSelectedModel] = useState<MLModel | null>(null);
  const [activeModelId, setActiveModelId] = useState<string>('');

  const fetchModels = async () => {
    try {
      const data = await api.getModels();
      setModels(data);
      if (data.length > 0 && !activeModelId) {
        setActiveModelId(data[0].id);
      }
    } catch (err) {
      console.error('Error loading models:', err);
    }
  };

  useEffect(() => {
    fetchModels();
  }, []);

  const handleActivate = async (m: MLModel) => {
    try {
      await api.activateModel(m.id);
      setActiveModelId(m.id);
      alert(`Model '${m.name}' (${m.architecture}) is now active for live HAR inference.`);
    } catch (err: any) {
      alert(err.message || 'Failed to activate model');
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-md">
        <div>
          <h2 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
            <Cpu className="w-5 h-5 text-brand-400" />
            Model Registry & Benchmarking
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Machine learning classifiers (Random Forest, SVM, 1D CNN, CNN-GRU, Transformer) & Anomaly Detectors.
          </p>
        </div>

        <div className="flex items-center space-x-2 text-xs">
          <span className="text-slate-400">Active Inference Model:</span>
          <span className="font-mono font-bold text-brand-400 px-2.5 py-1 rounded-lg bg-brand-500/10 border border-brand-500/20">
            {models.find((m) => m.id === activeModelId)?.name || 'Default Classifier'}
          </span>
        </div>
      </div>

      {/* Models Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {models.map((m) => {
          const isActive = m.id === activeModelId;
          const metrics = m.metrics || {};
          const acc = metrics.accuracy !== undefined ? (metrics.accuracy * 100).toFixed(1) : '--';
          const f1 = metrics.f1_macro !== undefined ? (metrics.f1_macro * 100).toFixed(1) : '--';
          const lat = metrics.inference_latency_ms_per_sample || 1.8;

          return (
            <div
              key={m.id}
              className={`bg-slate-900 rounded-2xl p-5 border transition-all shadow-md flex flex-col justify-between ${
                isActive
                  ? 'border-brand-500/50 shadow-brand-500/10'
                  : 'border-slate-800 hover:border-slate-700'
              }`}
            >
              <div>
                <div className="flex items-start justify-between">
                  <div>
                    <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-brand-500/10 text-brand-400 border border-brand-500/20">
                      {m.architecture}
                    </span>
                    <h3 className="text-base font-bold text-white mt-2">{m.name}</h3>
                    <p className="text-[11px] text-slate-400 font-mono">v{m.version}</p>
                  </div>

                  {isActive && (
                    <span className="flex items-center gap-1 text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 animate-pulse">
                      <CheckCircle2 className="w-3 h-3" /> Active
                    </span>
                  )}
                </div>

                {/* Metrics Breakdown */}
                <div className="grid grid-cols-3 gap-2 my-4 bg-slate-950/60 p-3 rounded-xl border border-slate-800/80 text-center">
                  <div>
                    <span className="text-[10px] text-slate-400 uppercase">Accuracy</span>
                    <p className="text-base font-black text-white mt-0.5">{acc}%</p>
                  </div>
                  <div>
                    <span className="text-[10px] text-slate-400 uppercase">Macro F1</span>
                    <p className="text-base font-black text-white mt-0.5">{f1}%</p>
                  </div>
                  <div>
                    <span className="text-[10px] text-slate-400 uppercase">Latency</span>
                    <p className="text-base font-black text-white mt-0.5">{lat}ms</p>
                  </div>
                </div>

                {/* Training Environment tags */}
                <div className="text-xs text-slate-400 space-y-1">
                  <div className="flex items-center justify-between text-[11px]">
                    <span>Training Envs:</span>
                    <span className="text-slate-200 font-medium">
                      {m.training_environments?.join(', ') || 'Office'}
                    </span>
                  </div>
                  <div className="flex items-center justify-between text-[11px]">
                    <span>Classes:</span>
                    <span className="text-slate-200 font-mono">{m.classes?.length || 6} categories</span>
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex items-center space-x-2 pt-4 border-t border-slate-800/80 mt-4">
                <button
                  onClick={() => setSelectedModel(m)}
                  className="flex-1 py-2 px-3 rounded-xl text-xs font-bold bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 flex items-center justify-center gap-1.5 transition-colors"
                >
                  <Eye className="w-3.5 h-3.5 text-brand-400" />
                  <span>View Metrics</span>
                </button>

                {!isActive && (
                  <button
                    onClick={() => handleActivate(m)}
                    className="py-2 px-3 rounded-xl text-xs font-bold bg-brand-600 hover:bg-brand-500 text-white shadow-md transition-colors"
                  >
                    Activate
                  </button>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Model Inspection & Confusion Matrix Modal */}
      <Modal
        isOpen={!!selectedModel}
        onClose={() => setSelectedModel(null)}
        title={`Evaluation Metrics: ${selectedModel?.name || ''}`}
        maxWidth="max-w-3xl"
      >
        {selectedModel && (
          <div className="space-y-5 text-xs">
            {/* Top Stats */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 bg-slate-950 p-4 rounded-xl border border-slate-800 text-center">
              <div>
                <span className="text-[11px] text-slate-400">Accuracy</span>
                <p className="text-xl font-black text-white">
                  {((selectedModel.metrics?.accuracy || 0) * 100).toFixed(2)}%
                </p>
              </div>
              <div>
                <span className="text-[11px] text-slate-400">Macro F1</span>
                <p className="text-xl font-black text-white">
                  {((selectedModel.metrics?.f1_macro || 0) * 100).toFixed(2)}%
                </p>
              </div>
              <div>
                <span className="text-[11px] text-slate-400">Weighted F1</span>
                <p className="text-xl font-black text-white">
                  {((selectedModel.metrics?.f1_weighted || 0) * 100).toFixed(2)}%
                </p>
              </div>
              <div>
                <span className="text-[11px] text-slate-400">Inference Latency</span>
                <p className="text-xl font-black text-white">
                  {selectedModel.metrics?.inference_latency_ms_per_sample || 1.8} ms
                </p>
              </div>
            </div>

            {/* Confusion Matrix Visualizer */}
            {selectedModel.metrics?.confusion_matrix && selectedModel.metrics?.labels && (
              <div>
                <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-2">
                  Confusion Matrix
                </h4>
                <div className="overflow-x-auto bg-slate-950 p-4 rounded-xl border border-slate-800">
                  <table className="w-full text-center font-mono text-[11px]">
                    <thead>
                      <tr>
                        <th className="p-1 text-slate-500 text-left">True \ Pred</th>
                        {selectedModel.metrics.labels.map((lbl, idx) => (
                          <th key={idx} className="p-1 text-brand-400 truncate max-w-[80px]">
                            {lbl}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {selectedModel.metrics.confusion_matrix.map((row, rIdx) => (
                        <tr key={rIdx}>
                          <td className="p-1 font-semibold text-slate-300 text-left">
                            {selectedModel.metrics.labels?.[rIdx]}
                          </td>
                          {row.map((val, cIdx) => {
                            const isDiagonal = rIdx === cIdx;
                            return (
                              <td
                                key={cIdx}
                                className={`p-1.5 rounded ${
                                  isDiagonal
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
                            );
                          })}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* Per-Class Report Table */}
            {selectedModel.metrics?.per_class && (
              <div>
                <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-2">
                  Per-Class Performance
                </h4>
                <div className="overflow-x-auto bg-slate-950 rounded-xl border border-slate-800">
                  <table className="w-full text-left font-mono text-[11px]">
                    <thead className="border-b border-slate-800 text-slate-400">
                      <tr>
                        <th className="p-2.5">Class Label</th>
                        <th className="p-2.5">Precision</th>
                        <th className="p-2.5">Recall</th>
                        <th className="p-2.5">F1-Score</th>
                        <th className="p-2.5 text-right">Support</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/60">
                      {Object.entries(selectedModel.metrics.per_class).map(([clsName, stats]) => (
                        <tr key={clsName}>
                          <td className="p-2.5 text-white font-semibold">{clsName}</td>
                          <td className="p-2.5 text-slate-300">{((stats.precision || 0) * 100).toFixed(1)}%</td>
                          <td className="p-2.5 text-slate-300">{((stats.recall || 0) * 100).toFixed(1)}%</td>
                          <td className="p-2.5 text-brand-300 font-bold">{((stats.f1_score || 0) * 100).toFixed(1)}%</td>
                          <td className="p-2.5 text-slate-400 text-right">{stats.support}</td>
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
