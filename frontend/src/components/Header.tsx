import React from 'react';
import { Activity, Shield, Wifi, RefreshCw } from 'lucide-react';
import { HealthStatus } from '../types';

interface HeaderProps {
  title: string;
  subtitle?: string;
  isWsConnected: boolean;
  health: HealthStatus | null;
  activeEnvironment?: string;
  onRefresh?: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  title,
  subtitle,
  isWsConnected,
  health,
  activeEnvironment = 'Office',
  onRefresh,
}) => {
  return (
    <header className="h-16 px-6 border-b border-slate-800 bg-slate-900/60 backdrop-blur-md flex items-center justify-between sticky top-0 z-30">
      <div>
        <h2 className="text-lg font-bold text-white tracking-tight flex items-center gap-2">
          {title}
        </h2>
        {subtitle && <p className="text-xs text-slate-400 font-medium">{subtitle}</p>}
      </div>

      <div className="flex items-center space-x-3 text-xs">
        {/* Environment Badge */}
        <div className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-slate-800 border border-slate-700 text-slate-300">
          <span className="text-slate-400">Environment:</span>
          <span className="font-semibold text-brand-400">{activeEnvironment}</span>
        </div>

        {/* Demo Mode / Synthetic Tag */}
        <div className="flex items-center space-x-1 px-2.5 py-1.5 rounded-lg bg-brand-950/80 border border-brand-800/60 text-brand-300">
          <span className="w-2 h-2 rounded-full bg-brand-400 animate-pulse"></span>
          <span className="font-medium tracking-wide">Demo Mode (Synthetic Data)</span>
        </div>

        {/* WebSocket Stream Status */}
        <div
          className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg border font-medium ${
            isWsConnected
              ? 'bg-emerald-950/40 text-emerald-400 border-emerald-800/60'
              : 'bg-rose-950/40 text-rose-400 border-rose-800/60'
          }`}
        >
          <span
            className={`w-2 h-2 rounded-full ${
              isWsConnected ? 'bg-emerald-400 animate-ping' : 'bg-rose-400'
            }`}
          ></span>
          <span>{isWsConnected ? 'WS Replay Active' : 'WS Disconnected'}</span>
        </div>

        {/* Refresh Button */}
        {onRefresh && (
          <button
            onClick={onRefresh}
            className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-300 transition-colors"
            title="Refresh Data"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        )}
      </div>
    </header>
  );
};
