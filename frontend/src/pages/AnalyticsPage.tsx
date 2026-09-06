import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
  CartesianGrid,
  Legend
} from 'recharts';
import {
  BarChart3,
  TrendingUp,
  PieChart as PieIcon,
  Cpu,
  Clock,
  Activity,
  AlertTriangle,
  Layers,
  Sparkles
} from 'lucide-react';

const COLORS = ['#0ea5e9', '#10b981', '#f59e0b', '#8b5cf6', '#f43f5e', '#06b6d4', '#64748b'];

export const AnalyticsPage: React.FC = () => {
  const [analytics, setAnalytics] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);

  const fetchAnalytics = async () => {
    try {
      setLoading(true);
      const data = await api.getAnalyticsSummary();
      setAnalytics(data);
    } catch (err) {
      console.error('Failed to load analytics:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalytics();
  }, []);

  if (loading || !analytics) {
    return (
      <div className="flex items-center justify-center h-64 text-slate-400 text-xs">
        Loading analytics intelligence telemetry...
      </div>
    );
  }

  const { metrics_summary, activity_distribution, environment_distribution, model_benchmarks, recent_trend } = analytics;

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-md">
        <h2 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
          <BarChart3 className="w-5 h-5 text-brand-400" />
          Intelligence Analytics & Performance Benchmarks
        </h2>
        <p className="text-xs text-slate-400 mt-0.5">
          Longitudinal activity distribution, cross-environment sensing breakdown, and comparative model accuracy.
        </p>
      </div>

      {/* Summary KPI Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
        <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl shadow-sm">
          <span className="text-[11px] text-slate-400 font-medium">Total Inferences</span>
          <p className="text-2xl font-black text-white mt-1">{metrics_summary.total_inferences}</p>
        </div>
        <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl shadow-sm">
          <span className="text-[11px] text-slate-400 font-medium">Events Logged</span>
          <p className="text-2xl font-black text-brand-400 mt-1">{metrics_summary.total_events}</p>
        </div>
        <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl shadow-sm">
          <span className="text-[11px] text-slate-400 font-medium">Anomalies Detected</span>
          <p className="text-2xl font-black text-amber-400 mt-1">{metrics_summary.total_anomalies}</p>
        </div>
        <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl shadow-sm">
          <span className="text-[11px] text-slate-400 font-medium">Active Environments</span>
          <p className="text-2xl font-black text-emerald-400 mt-1">{metrics_summary.active_environments}</p>
        </div>
        <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl shadow-sm">
          <span className="text-[11px] text-slate-400 font-medium">Trained Models</span>
          <p className="text-2xl font-black text-purple-400 mt-1">{metrics_summary.registered_models}</p>
        </div>
        <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl shadow-sm">
          <span className="text-[11px] text-slate-400 font-medium">Anomaly Rate</span>
          <p className="text-2xl font-black text-rose-400 mt-1">{metrics_summary.anomaly_rate_percent}%</p>
        </div>
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 1. Activity Distribution Pie */}
        <div className="bg-slate-900 border border-slate-800 p-5 rounded-2xl shadow-md flex flex-col justify-between">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
              <PieIcon className="w-4 h-4 text-brand-400" />
              Activity Class Proportions
            </h3>
            <span className="text-[10px] font-mono text-slate-400">Relative Occurrences</span>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={activity_distribution}
                  dataKey="count"
                  nameKey="activity"
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  innerRadius={45}
                  paddingAngle={4}
                  label={({ activity, percent }) => `${activity} (${(percent * 100).toFixed(0)}%)`}
                >
                  {activity_distribution.map((entry: any, index: number) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* 2. Model Accuracy Benchmarks */}
        <div className="bg-slate-900 border border-slate-800 p-5 rounded-2xl shadow-md flex flex-col justify-between">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
              <Cpu className="w-4 h-4 text-emerald-400" />
              Model Architecture Benchmarks (Accuracy vs F1)
            </h3>
            <span className="text-[10px] font-mono text-slate-400">Validated Metrics</span>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={model_benchmarks} margin={{ top: 10, right: 10, left: -20, bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="architecture" stroke="#64748b" fontSize={11} interval={0} angle={-15} textAnchor="end" />
                <YAxis stroke="#64748b" fontSize={11} domain={[0, 1]} tickFormatter={(v) => `${(v * 100).toFixed(0)}%`} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
                  formatter={(val: any) => [`${((val as number) * 100).toFixed(1)}%`]}
                />
                <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />
                <Bar dataKey="accuracy" name="Accuracy" fill="#0ea5e9" radius={[4, 4, 0, 0]} />
                <Bar dataKey="f1_macro" name="Macro F1" fill="#10b981" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* 3. Temporal Confidence and Anomaly Trend */}
      <div className="bg-slate-900 border border-slate-800 p-5 rounded-2xl shadow-md">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
            <TrendingUp className="w-4 h-4 text-accent-cyan" />
            Temporal Confidence & Anomaly Score Trajectory
          </h3>
          <span className="text-[10px] font-mono text-slate-400">Recent Inferences Time-Series</span>
        </div>

        <div className="h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={recent_trend} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="time" stroke="#64748b" fontSize={11} />
              <YAxis stroke="#64748b" fontSize={11} domain={[0, 1]} />
              <Tooltip
                contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
              />
              <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '8px' }} />
              <Line type="monotone" dataKey="confidence" name="Model Confidence" stroke="#0ea5e9" strokeWidth={2.5} dot={{ r: 3 }} />
              <Line type="monotone" dataKey="anomaly_score" name="Anomaly Index" stroke="#f43f5e" strokeWidth={2} dot={{ r: 3 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};
