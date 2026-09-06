import React from 'react';
import {
  Activity,
  UserCheck,
  UserX,
  AlertTriangle,
  Zap,
  Gauge,
  CheckCircle2
} from 'lucide-react';

interface ActivityCardProps {
  activity: string;
  confidence: number;
  presence: string;
  presenceConfidence: number;
  anomalyScore: number;
  isAnomaly: boolean;
  dynamicEnergy?: number;
  isSynthetic?: boolean;
}

export const ActivityCard: React.FC<ActivityCardProps> = ({
  activity = 'Walking',
  confidence = 0.94,
  presence = 'Present',
  presenceConfidence = 0.98,
  anomalyScore = 0.08,
  isAnomaly = false,
  dynamicEnergy = 0.45,
  isSynthetic = true,
}) => {
  const isFall = activity.toLowerCase().includes('fall');
  const isAbsent = presence.toLowerCase() === 'absent' || activity.toLowerCase() === 'empty';

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      {/* 1. Primary HAR Activity Card */}
      <div
        className={`p-5 rounded-2xl border transition-all duration-300 relative overflow-hidden flex flex-col justify-between ${
          isFall
            ? 'bg-rose-950/40 border-rose-600/60 shadow-lg shadow-rose-900/30'
            : isAbsent
            ? 'bg-slate-900/80 border-slate-800'
            : 'bg-gradient-to-b from-slate-900 to-slate-950 border-slate-800 shadow-md'
        }`}
      >
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
            <Activity className="w-4 h-4 text-brand-400" />
            Detected Human Activity
          </span>
          <span
            className={`text-xs font-mono font-bold px-2.5 py-0.5 rounded-full ${
              isFall
                ? 'bg-rose-500/20 text-rose-300 border border-rose-500/40 animate-pulse'
                : 'bg-brand-500/20 text-brand-300 border border-brand-500/30'
            }`}
          >
            {Math.round(confidence * 100)}% Conf.
          </span>
        </div>

        <div className="my-4">
          <div className="text-3xl font-black tracking-tight text-white flex items-center gap-3">
            {activity}
            {isFall && (
              <span className="text-xs px-2 py-1 rounded bg-rose-600 text-white font-semibold uppercase tracking-wider animate-bounce">
                Impact Alert
              </span>
            )}
          </div>
          <div className="w-full bg-slate-800 rounded-full h-2 mt-3 overflow-hidden">
            <div
              className={`h-full rounded-full transition-all duration-300 ${
                isFall ? 'bg-rose-500' : 'bg-brand-500'
              }`}
              style={{ width: `${Math.min(100, Math.max(5, confidence * 100))}%` }}
            ></div>
          </div>
        </div>

        <div className="flex items-center justify-between text-[11px] text-slate-400 border-t border-slate-800/80 pt-2.5">
          <span>Model: Real-time HAR</span>
          <span>Latency: ~1.8 ms</span>
        </div>
      </div>

      {/* 2. Presence Detection Card */}
      <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 flex flex-col justify-between shadow-md">
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
            {isAbsent ? (
              <UserX className="w-4 h-4 text-slate-400" />
            ) : (
              <UserCheck className="w-4 h-4 text-emerald-400" />
            )}
            Presence Detection
          </span>
          <span className="text-xs font-mono text-slate-400">
            {Math.round(presenceConfidence * 100)}%
          </span>
        </div>

        <div className="my-4">
          <div className="flex items-center space-x-2.5">
            <span
              className={`w-3.5 h-3.5 rounded-full ${
                isAbsent ? 'bg-slate-600' : 'bg-emerald-400 animate-pulse'
              }`}
            ></span>
            <span className="text-2xl font-extrabold text-white">{presence}</span>
          </div>
          <p className="text-xs text-slate-400 mt-2">
            {isAbsent
              ? 'No human presence motion detected in radio Fresnel zone.'
              : 'Active motion signature detected across subcarrier paths.'}
          </p>
        </div>

        <div className="flex items-center justify-between text-[11px] text-slate-400 border-t border-slate-800/80 pt-2.5">
          <span>Signal Doppler Energy</span>
          <span className="font-mono text-slate-300">{dynamicEnergy.toFixed(3)}</span>
        </div>
      </div>

      {/* 3. Anomaly Detection Card */}
      <div
        className={`p-5 rounded-2xl border flex flex-col justify-between shadow-md transition-all duration-300 ${
          isAnomaly
            ? 'bg-amber-950/40 border-amber-600/50'
            : 'bg-slate-900 border-slate-800'
        }`}
      >
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
            <Gauge className="w-4 h-4 text-accent-amber" />
            Anomaly Score
          </span>
          <span
            className={`text-xs font-mono font-bold px-2.5 py-0.5 rounded-full ${
              isAnomaly
                ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                : 'bg-emerald-500/10 text-emerald-400'
            }`}
          >
            {isAnomaly ? 'Anomalous Motion' : 'Normal Pattern'}
          </span>
        </div>

        <div className="my-4">
          <div className="text-2xl font-extrabold text-white flex items-baseline gap-2">
            <span>{(anomalyScore * 100).toFixed(1)}%</span>
            <span className="text-xs text-slate-400 font-normal">Score Index</span>
          </div>
          <div className="w-full bg-slate-800 rounded-full h-2 mt-3 overflow-hidden">
            <div
              className={`h-full rounded-full transition-all duration-300 ${
                anomalyScore > 0.5 ? 'bg-amber-500' : 'bg-emerald-500'
              }`}
              style={{ width: `${Math.min(100, Math.max(5, anomalyScore * 100))}%` }}
            ></div>
          </div>
        </div>

        <div className="flex items-center justify-between text-[11px] text-slate-400 border-t border-slate-800/80 pt-2.5">
          <span>Threshold: 50.0%</span>
          <span>Status: {isAnomaly ? 'Flagged' : 'Passed'}</span>
        </div>
      </div>
    </div>
  );
};
