import React from 'react';
import {
  LayoutDashboard,
  Radio,
  Building2,
  Database,
  Cpu,
  FlaskConical,
  BarChart3,
  Settings,
  ShieldCheck,
  Wifi
} from 'lucide-react';

interface SidebarProps {
  activeTab: string;
  onSelectTab: (tab: string) => void;
}

const NAV_ITEMS = [
  { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { id: 'live', label: 'Live Analysis', icon: Radio, badge: 'Stream' },
  { id: 'environments', label: 'Environments', icon: Building2 },
  { id: 'datasets', label: 'Datasets', icon: Database },
  { id: 'models', label: 'Models & Registry', icon: Cpu },
  { id: 'experiments', label: 'Experiments', icon: FlaskConical },
  { id: 'analytics', label: 'Analytics', icon: BarChart3 },
  { id: 'settings', label: 'Settings', icon: Settings },
];

export const Sidebar: React.FC<SidebarProps> = ({ activeTab, onSelectTab }) => {
  return (
    <aside className="w-64 bg-slate-900 border-r border-slate-800 flex flex-col justify-between shrink-0 select-none">
      <div>
        {/* Brand Header */}
        <div className="p-6 border-b border-slate-800 flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-brand-600 to-accent-cyan flex items-center justify-center shadow-lg shadow-brand-500/20">
            <Wifi className="w-5 h-5 text-white animate-pulse" />
          </div>
          <div>
            <h1 className="text-base font-bold tracking-tight text-white flex items-center gap-1.5">
              WiFiSense <span className="text-xs px-1.5 py-0.5 rounded bg-brand-500/20 text-brand-400 font-mono">AI</span>
            </h1>
            <p className="text-[11px] text-slate-400 font-medium tracking-wide">CSI Activity Intelligence</p>
          </div>
        </div>

        {/* Navigation Links */}
        <nav className="p-3 space-y-1">
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => onSelectTab(item.id)}
                className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-lg text-sm font-medium transition-all duration-150 ${
                  isActive
                    ? 'bg-brand-600/15 text-brand-400 border border-brand-500/30 shadow-sm'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                }`}
              >
                <div className="flex items-center space-x-3">
                  <Icon className={`w-4 h-4 ${isActive ? 'text-brand-400' : 'text-slate-400'}`} />
                  <span>{item.label}</span>
                </div>
                {item.badge && (
                  <span className="text-[10px] font-semibold uppercase px-1.5 py-0.5 rounded-full bg-accent-emerald/20 text-accent-emerald tracking-wider animate-pulse">
                    {item.badge}
                  </span>
                )}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Footer Info / Privacy Assurance */}
      <div className="p-4 border-t border-slate-800/80 m-3 rounded-xl bg-slate-950/60 border">
        <div className="flex items-start space-x-2.5">
          <ShieldCheck className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
          <div>
            <h4 className="text-xs font-semibold text-slate-300">Privacy Preserving</h4>
            <p className="text-[11px] text-slate-400 leading-tight mt-0.5">
              Numerical Wi-Fi CSI only. No cameras or biometric profiling.
            </p>
          </div>
        </div>
      </div>
    </aside>
  );
};
