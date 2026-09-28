import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import DashboardTab from './components/DashboardTab';
import MapTab from './components/MapTab';
import RegimesTab from './components/RegimesTab';
import ComparisonTab from './components/ComparisonTab';
import HeavyRainTab from './components/HeavyRainTab';
import VerificationTab from './components/VerificationTab';
import MethodologyTab from './components/MethodologyTab';
import AboutTab from './components/AboutTab';
import { fetchHealth } from './services/api';

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [backendStatus, setBackendStatus] = useState('checking');

  useEffect(() => {
    checkBackendHealth();
    const interval = setInterval(checkBackendHealth, 15000);
    return () => clearInterval(interval);
  }, []);

  const checkBackendHealth = async () => {
    try {
      const data = await fetchHealth();
      if (data && data.status === 'ok') {
        setBackendStatus('online');
      } else {
        setBackendStatus('offline');
      }
    } catch {
      setBackendStatus('offline');
    }
  };

  return (
    <div className="min-h-screen bg-[#090d16] text-slate-100 flex flex-col font-['Plus_Jakarta_Sans',sans-serif]">
      {/* Header & Navigation */}
      <Header
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        backendStatus={backendStatus}
      />

      {/* Main Active Page View */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {activeTab === 'dashboard' && <DashboardTab onNavigateToMap={() => setActiveTab('map')} />}
        {activeTab === 'map' && <MapTab />}
        {activeTab === 'regimes' && <RegimesTab />}
        {activeTab === 'comparison' && <ComparisonTab />}
        {activeTab === 'heavy' && <HeavyRainTab />}
        {activeTab === 'verification' && <VerificationTab />}
        {activeTab === 'methodology' && <MethodologyTab />}
        {activeTab === 'about' && <AboutTab />}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800/80 bg-slate-900/60 py-4 text-center text-xs text-slate-400 mt-auto">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-2">
          <span>Problem ID 26080 • Ministry of Earth Sciences (MoES) / NCMRWF</span>
          <span>Regime-Aware AI Monsoon Post-Processing System © 2026</span>
        </div>
      </footer>
    </div>
  );
}
