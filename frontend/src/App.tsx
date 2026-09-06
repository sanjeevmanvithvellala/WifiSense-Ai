import React, { useState, useEffect } from 'react';
import { Sidebar } from './components/Sidebar';
import { Header } from './components/Header';
import { DashboardPage } from './pages/DashboardPage';
import { LiveAnalysisPage } from './pages/LiveAnalysisPage';
import { EnvironmentsPage } from './pages/EnvironmentsPage';
import { DatasetsPage } from './pages/DatasetsPage';
import { ModelsPage } from './pages/ModelsPage';
import { ExperimentsPage } from './pages/ExperimentsPage';
import { AnalyticsPage } from './pages/AnalyticsPage';
import { SettingsPage } from './pages/SettingsPage';
import { useWebSocketReplay } from './hooks/useWebSocketReplay';
import { HealthStatus } from './types';
import { api } from './services/api';

export function App() {
  const [activeTab, setActiveTab] = useState<string>('dashboard');
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const { isConnected, lastFrame } = useWebSocketReplay();

  const fetchHealth = async () => {
    try {
      const data = await api.getHealth();
      setHealth(data);
    } catch (_) {}
  };

  useEffect(() => {
    fetchHealth();
    const interval = setInterval(fetchHealth, 5000);
    return () => clearInterval(interval);
  }, []);

  const getPageTitle = () => {
    switch (activeTab) {
      case 'dashboard':
        return { title: 'Activity Intelligence Dashboard', subtitle: 'Live Human Presence & Activity Classification' };
      case 'live':
        return { title: 'Live CSI Analysis & Replay', subtitle: 'Interactive Signal Processing and Spectrogram Stream' };
      case 'environments':
        return { title: 'Environment Management', subtitle: 'Room Profiles, Multipath Calibration & Domain Settings' };
      case 'datasets':
        return { title: 'Dataset Registry & Adapters', subtitle: 'Public, Uploaded & Synthetic CSI Sources' };
      case 'models':
        return { title: 'Machine Learning Models', subtitle: 'Classifiers, Anomaly Detectors & Performance Checkpoints' };
      case 'experiments':
        return { title: 'Experiment Engine', subtitle: 'Cross-Environment & Adaptation Benchmarks' };
      case 'analytics':
        return { title: 'Analytics & Insights', subtitle: 'Longitudinal Trends & Performance Distributions' };
      case 'settings':
        return { title: 'Platform Settings', subtitle: 'Configuration, Filter Parameters & Privacy Controls' };
      default:
        return { title: 'WiFiSense AI', subtitle: 'Human Activity Intelligence Platform' };
    }
  };

  const { title, subtitle } = getPageTitle();

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-slate-950 font-sans text-slate-100">
      {/* Sidebar */}
      <Sidebar activeTab={activeTab} onSelectTab={setActiveTab} />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col h-full overflow-hidden">
        <Header
          title={title}
          subtitle={subtitle}
          isWsConnected={isConnected}
          health={health}
          activeEnvironment={lastFrame?.environment || 'Office'}
          onRefresh={fetchHealth}
        />

        <main className="flex-1 overflow-y-auto p-6 bg-slate-950/40">
          <div className="max-w-7xl mx-auto pb-12">
            {activeTab === 'dashboard' && (
              <DashboardPage
                lastFrame={lastFrame}
                health={health}
                onNavigateToLive={() => setActiveTab('live')}
              />
            )}
            {activeTab === 'live' && <LiveAnalysisPage lastFrame={lastFrame} />}
            {activeTab === 'environments' && <EnvironmentsPage />}
            {activeTab === 'datasets' && <DatasetsPage />}
            {activeTab === 'models' && <ModelsPage />}
            {activeTab === 'experiments' && <ExperimentsPage />}
            {activeTab === 'analytics' && <AnalyticsPage />}
            {activeTab === 'settings' && <SettingsPage />}
          </div>
        </main>
      </div>
    </div>
  );
}

export default App;
