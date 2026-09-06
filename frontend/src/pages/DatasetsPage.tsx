import React, { useState, useEffect } from 'react';
import { Dataset } from '../types';
import { api } from '../services/api';
import { Modal } from '../components/Modal';
import {
  Database,
  Search,
  CheckCircle2,
  AlertCircle,
  FileCode,
  Upload,
  Eye,
  Info,
  Layers,
  Sparkles,
  ExternalLink,
  ShieldCheck
} from 'lucide-react';

export const DatasetsPage: React.FC = () => {
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [selectedDataset, setSelectedDataset] = useState<Dataset | null>(null);
  const [inspectData, setInspectData] = useState<any>(null);
  const [inspectLoading, setInspectLoading] = useState<boolean>(false);

  // Upload modal state
  const [isUploadModalOpen, setIsUploadModalOpen] = useState<boolean>(false);
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [uploadEnv, setUploadEnv] = useState<string>('Office');
  const [uploadAct, setUploadAct] = useState<string>('Walking');
  const [uploadStatus, setUploadStatus] = useState<string>('');

  const fetchDatasets = async () => {
    try {
      const data = await api.getDatasets();
      setDatasets(data);
    } catch (err) {
      console.error('Error loading datasets:', err);
    }
  };

  useEffect(() => {
    fetchDatasets();
  }, []);

  const handleInspect = async (ds: Dataset) => {
    setSelectedDataset(ds);
    setInspectLoading(true);
    try {
      const info = await api.inspectDataset(ds.id);
      setInspectData(info);
    } catch (err) {
      console.error('Inspection error:', err);
    } finally {
      setInspectLoading(false);
    }
  };

  const handleFileUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!uploadFile) return;
    try {
      setUploadStatus('Uploading and parsing CSI matrix...');
      await api.uploadCSIFile(uploadFile, uploadEnv, uploadAct);
      setUploadStatus('Upload and validation successful!');
      setTimeout(() => {
        setIsUploadModalOpen(false);
        setUploadStatus('');
        setUploadFile(null);
        fetchDatasets();
      }, 1500);
    } catch (err: any) {
      setUploadStatus(`Upload error: ${err.message}`);
    }
  };

  const filtered = datasets.filter(
    (d) =>
      d.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      d.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
      d.adapter_id.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-md">
        <div>
          <h2 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
            <Database className="w-5 h-5 text-brand-400" />
            Dataset Management & Registry
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Pluggable adapter architecture for public, locally recorded, and synthetic demo CSI datasets.
          </p>
        </div>

        <button
          onClick={() => setIsUploadModalOpen(true)}
          className="flex items-center space-x-2 px-4 py-2.5 rounded-xl text-xs font-bold bg-brand-600 hover:bg-brand-500 text-white shadow-md transition-colors"
        >
          <Upload className="w-4 h-4" />
          <span>Upload Custom CSI File</span>
        </button>
      </div>

      {/* Search Bar */}
      <div className="relative">
        <Search className="w-4 h-4 text-slate-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
        <input
          type="text"
          placeholder="Filter datasets by name, adapter ID, or activity..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="w-full bg-slate-900 border border-slate-800 rounded-xl pl-10 pr-4 py-2.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-brand-500"
        />
      </div>

      {/* Datasets Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden shadow-md">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-950 border-b border-slate-800 text-slate-400 font-semibold uppercase tracking-wider">
              <tr>
                <th className="py-3.5 px-4">Dataset Name</th>
                <th className="py-3.5 px-4">Data Nature</th>
                <th className="py-3.5 px-4">Dimensions</th>
                <th className="py-3.5 px-4">Sampling Rate</th>
                <th className="py-3.5 px-4">Activities</th>
                <th className="py-3.5 px-4">Adapter Status</th>
                <th className="py-3.5 px-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/80">
              {filtered.map((ds) => (
                <tr key={ds.id} className="hover:bg-slate-850/50 transition-colors">
                  <td className="py-4 px-4 font-semibold text-white">
                    <div className="flex items-center space-x-2.5">
                      <div className="w-7 h-7 rounded-lg bg-brand-500/10 border border-brand-500/20 flex items-center justify-center shrink-0">
                        <Layers className="w-3.5 h-3.5 text-brand-400" />
                      </div>
                      <div>
                        <div className="font-bold text-white">{ds.name}</div>
                        <div className="text-[10px] text-slate-400 font-mono">{ds.id}</div>
                      </div>
                    </div>
                  </td>

                  <td className="py-4 px-4">
                    {ds.is_synthetic ? (
                      <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider bg-brand-500/20 text-brand-300 border border-brand-500/30">
                        <Sparkles className="w-3 h-3" /> Synthetic Demo
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider bg-purple-500/20 text-purple-300 border border-purple-500/30">
                        <ShieldCheck className="w-3 h-3" /> Real Dataset
                      </span>
                    )}
                  </td>

                  <td className="py-4 px-4 font-mono text-slate-300">
                    {ds.subcarriers} subcarriers | {ds.antennas} ant | {ds.bandwidth}MHz
                  </td>

                  <td className="py-4 px-4 font-mono text-slate-300">{ds.sampling_rate} Hz</td>

                  <td className="py-4 px-4">
                    <div className="flex flex-wrap gap-1 max-w-xs">
                      {ds.activities.slice(0, 3).map((act, i) => (
                        <span
                          key={i}
                          className="px-1.5 py-0.5 rounded bg-slate-800 text-[10px] text-slate-300"
                        >
                          {act}
                        </span>
                      ))}
                      {ds.activities.length > 3 && (
                        <span className="px-1.5 py-0.5 rounded bg-slate-800 text-[10px] text-slate-400 font-mono">
                          +{ds.activities.length - 3}
                        </span>
                      )}
                    </div>
                  </td>

                  <td className="py-4 px-4">
                    <span
                      className={`inline-flex items-center gap-1 text-[11px] font-medium ${
                        ds.status.includes('Available') || ds.status === 'Ready'
                          ? 'text-emerald-400'
                          : 'text-amber-400'
                      }`}
                    >
                      {ds.status.includes('Available') || ds.status === 'Ready' ? (
                        <CheckCircle2 className="w-3.5 h-3.5" />
                      ) : (
                        <Info className="w-3.5 h-3.5" />
                      )}
                      {ds.status}
                    </span>
                  </td>

                  <td className="py-4 px-4 text-right">
                    <button
                      onClick={() => handleInspect(ds)}
                      className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 font-medium inline-flex items-center gap-1.5 transition-colors"
                    >
                      <Eye className="w-3.5 h-3.5 text-brand-400" />
                      <span>Inspect</span>
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Dataset Inspection Modal */}
      <Modal
        isOpen={!!selectedDataset}
        onClose={() => setSelectedDataset(null)}
        title={`Dataset Inspection: ${selectedDataset?.name || ''}`}
        maxWidth="max-w-3xl"
      >
        {inspectLoading ? (
          <div className="text-center py-12 text-slate-400">Loading dataset inspection metadata...</div>
        ) : inspectData ? (
          <div className="space-y-5 text-xs">
            {/* Tag alert */}
            <div
              className={`p-3 rounded-xl border flex items-center justify-between ${
                inspectData.is_synthetic
                  ? 'bg-brand-950/40 border-brand-800/60 text-brand-300'
                  : 'bg-purple-950/40 border-purple-800/60 text-purple-300'
              }`}
            >
              <div className="flex items-center space-x-2">
                <Info className="w-4 h-4" />
                <span className="font-semibold">
                  {inspectData.is_synthetic
                    ? 'Explicit Label: Synthetic Demo Data (Generated for validation & offline demo)'
                    : 'Real Experimental Dataset Adapter Specification'}
                </span>
              </div>
              <span className="font-mono text-[11px]">{inspectData.adapter_id}</span>
            </div>

            {/* Dimensional Specifications */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 bg-slate-950 p-4 rounded-xl border border-slate-800">
              <div>
                <span className="text-[11px] text-slate-400">Subcarriers:</span>
                <p className="text-base font-black text-white">{inspectData.subcarriers}</p>
              </div>
              <div>
                <span className="text-[11px] text-slate-400">Antennas:</span>
                <p className="text-base font-black text-white">{inspectData.antennas}</p>
              </div>
              <div>
                <span className="text-[11px] text-slate-400">Sampling Rate:</span>
                <p className="text-base font-black text-white">{inspectData.sampling_rate} Hz</p>
              </div>
              <div>
                <span className="text-[11px] text-slate-400">Bandwidth:</span>
                <p className="text-base font-black text-white">{inspectData.bandwidth} MHz</p>
              </div>
            </div>

            {/* Activities & Environments */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="bg-slate-950 p-3 rounded-xl border border-slate-800">
                <h4 className="text-[11px] font-bold text-slate-300 uppercase tracking-wider mb-2">
                  Recognized Activities ({inspectData.activities?.length || 0})
                </h4>
                <div className="flex flex-wrap gap-1.5">
                  {inspectData.activities?.map((a: string, i: number) => (
                    <span key={i} className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 text-[11px]">
                      {a}
                    </span>
                  ))}
                </div>
              </div>

              <div className="bg-slate-950 p-3 rounded-xl border border-slate-800">
                <h4 className="text-[11px] font-bold text-slate-300 uppercase tracking-wider mb-2">
                  Supported Environments ({inspectData.environments?.length || 0})
                </h4>
                <div className="flex flex-wrap gap-1.5">
                  {inspectData.environments?.map((e: string, i: number) => (
                    <span key={i} className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 text-[11px]">
                      {e}
                    </span>
                  ))}
                </div>
              </div>
            </div>

            {/* Sample Matrix Preview */}
            {inspectData.sample_previews && inspectData.sample_previews.length > 0 && (
              <div>
                <h4 className="text-xs font-bold text-slate-300 mb-2">
                  Sample CSI Numerical Matrix Preview (First Sample)
                </h4>
                <div className="bg-slate-950 p-3 rounded-xl border border-slate-800 font-mono text-[10px] text-brand-300 max-h-36 overflow-auto">
                  {inspectData.sample_previews[0].preview_amplitude?.slice(0, 5).map((row: number[], idx: number) => (
                    <div key={idx} className="truncate">
                      [{row.slice(0, 12).map((v) => v.toFixed(2)).join(', ')}...]
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        ) : null}
      </Modal>

      {/* Upload Custom File Modal */}
      <Modal
        isOpen={isUploadModalOpen}
        onClose={() => setIsUploadModalOpen(false)}
        title="Upload Custom Wi-Fi CSI File (CSV / NPY)"
      >
        <form onSubmit={handleFileUpload} className="space-y-4 text-xs">
          <div>
            <label className="block text-slate-300 font-semibold mb-1">Select CSI File</label>
            <input
              type="file"
              required
              accept=".csv,.npy,.npz,.txt"
              onChange={(e) => setUploadFile(e.target.files ? e.target.files[0] : null)}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white file:mr-4 file:py-1 file:px-3 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:bg-brand-600 file:text-white hover:file:bg-brand-500"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-slate-300 font-semibold mb-1">Environment Type</label>
              <input
                type="text"
                value={uploadEnv}
                onChange={(e) => setUploadEnv(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white focus:outline-none focus:border-brand-500"
              />
            </div>
            <div>
              <label className="block text-slate-300 font-semibold mb-1">Activity Label</label>
              <input
                type="text"
                value={uploadAct}
                onChange={(e) => setUploadAct(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white focus:outline-none focus:border-brand-500"
              />
            </div>
          </div>

          {uploadStatus && (
            <div className="p-3 rounded-xl bg-brand-950/60 border border-brand-800 text-brand-300 font-medium">
              {uploadStatus}
            </div>
          )}

          <div className="flex justify-end space-x-3 pt-4 border-t border-slate-800">
            <button
              type="button"
              onClick={() => setIsUploadModalOpen(false)}
              className="px-4 py-2 rounded-xl text-slate-400 hover:text-white"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={!uploadFile}
              className="px-5 py-2 rounded-xl font-bold bg-brand-600 hover:bg-brand-500 disabled:opacity-50 text-white shadow-md"
            >
              Parse & Upload
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
