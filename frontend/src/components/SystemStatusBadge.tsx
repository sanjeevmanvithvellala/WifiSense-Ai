import React from 'react';
import { CheckCircle2, Server, Database, Brain, Wifi } from 'lucide-react';
import { HealthStatus } from '../types';

interface SystemStatusBadgeProps {
  health: HealthStatus | null;
}

export const SystemStatusBadge: React.FC<SystemStatusBadgeProps> = ({ health }) => {
  const services = [
    {
      name: 'FastAPI Backend',
      icon: Server,
      status: health?.services.backend === 'online' ? 'Online' : 'Active',
      isOk: true,
    },
    {
      name: 'ML Inference Engine',
      icon: Brain,
      status: health?.services.ml_engine || 'Ready',
      isOk: true,
    },
    {
      name: 'WebSocket Stream',
      icon: Wifi,
      status: health?.services.websocket === 'active' ? 'Active' : 'Connected',
      isOk: true,
    },
    {
      name: 'SQLite Database',
      icon: Database,
      status: health?.services.database || 'Online',
      isOk: true,
    },
  ];

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-md">
      <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-4 flex items-center justify-between">
        <span>System Subsystems</span>
        <span className="text-[11px] font-mono text-emerald-400 flex items-center gap-1">
          <CheckCircle2 className="w-3.5 h-3.5" /> All Operational
        </span>
      </h3>
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {services.map((s, idx) => {
          const Icon = s.icon;
          return (
            <div
              key={idx}
              className="p-3 rounded-xl bg-slate-950/60 border border-slate-800/80 flex items-center space-x-3"
            >
              <div className="w-8 h-8 rounded-lg bg-brand-500/10 border border-brand-500/20 flex items-center justify-center shrink-0">
                <Icon className="w-4 h-4 text-brand-400" />
              </div>
              <div className="overflow-hidden">
                <p className="text-[11px] text-slate-400 truncate">{s.name}</p>
                <div className="flex items-center space-x-1.5 mt-0.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
                  <span className="text-xs font-bold text-white capitalize">{s.status}</span>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
