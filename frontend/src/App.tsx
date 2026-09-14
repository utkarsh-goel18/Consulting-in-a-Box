import React, { useState, useEffect } from 'react';
import { Navbar } from './components/layout/Navbar';
import { DashboardPage } from './pages/DashboardPage';
import { DatasetsPage } from './pages/DatasetsPage';
import { AnalysisPage } from './pages/AnalysisPage';
import { InsightsPage } from './pages/InsightsPage';
import { ScenariosPage } from './pages/ScenariosPage';
import { ReportsPage } from './pages/ReportsPage';
import { SettingsPage } from './pages/SettingsPage';
import { EvidenceModal } from './components/common/EvidenceModal';
import { ConsultingDashboard, EvidenceDetail } from './types';
import { bootstrapDemo, getEvidenceDetail } from './api/client';
import { Loader2, CheckCircle2 } from 'lucide-react';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<string>('dashboard');
  const [dashboardData, setDashboardData] = useState<ConsultingDashboard | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [demoLoading, setDemoLoading] = useState<boolean>(false);
  const [demoProgressStep, setDemoProgressStep] = useState<string>('');
  
  const [activeEvidence, setActiveEvidence] = useState<EvidenceDetail | null>(null);

  // Stepped sequence for realistic demo progress feedback
  const demoSequence = [
    'Profiling data...',
    'Building data model...',
    'Calculating KPIs...',
    'Analysing drivers...',
    'Detecting anomalies...',
    'Generating insights...',
    'Preparing recommendations...'
  ];

  const handleRunDemo = async () => {
    try {
      setDemoLoading(true);
      for (const step of demoSequence) {
        setDemoProgressStep(step);
        await new Promise((resolve) => setTimeout(resolve, 280));
      }
      const data = await bootstrapDemo();
      setDashboardData(data);
      setActiveTab('dashboard');
    } catch (err: any) {
      alert(`Demo bootstrap failed: ${err.message}`);
    } finally {
      setDemoLoading(false);
      setDemoProgressStep('');
    }
  };

  useEffect(() => {
    // Initial auto-load
    bootstrapDemo()
      .then((data) => setDashboardData(data))
      .catch((err) => console.error('Initial demo load failed:', err))
      .finally(() => setLoading(false));
  }, []);

  const handleOpenEvidence = async (evidenceId: string) => {
    try {
      const ev = await getEvidenceDetail(evidenceId);
      setActiveEvidence(ev);
    } catch (err: any) {
      alert(`Failed to load evidence audit: ${err.message}`);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-900 text-white flex flex-col items-center justify-center space-y-4">
        <div className="w-12 h-12 bg-blue-600 rounded-lg flex items-center justify-center font-bold text-xl shadow-lg animate-pulse">
          CB
        </div>
        <div className="flex items-center space-x-2 text-slate-300 text-sm">
          <Loader2 className="w-4 h-4 animate-spin text-blue-400" />
          <span>Initializing Consulting in a Box Platform...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col font-sans">
      
      {/* Navigation Header */}
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        onRunDemo={handleRunDemo}
        demoLoading={demoLoading}
        demoProgressStep={demoProgressStep}
      />

      {/* Main Page Body */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'dashboard' && dashboardData && (
          <DashboardPage
            data={dashboardData}
            onNavigate={setActiveTab}
            onViewEvidence={handleOpenEvidence}
          />
        )}

        {activeTab === 'datasets' && (
          <DatasetsPage />
        )}

        {activeTab === 'analysis' && (
          <AnalysisPage onPlanExecuted={() => setActiveTab('insights')} />
        )}

        {activeTab === 'insights' && dashboardData && (
          <InsightsPage
            data={dashboardData}
            onViewEvidence={handleOpenEvidence}
          />
        )}

        {activeTab === 'scenarios' && dashboardData && (
          <ScenariosPage data={dashboardData} />
        )}

        {activeTab === 'reports' && dashboardData && (
          <ReportsPage dashboardData={dashboardData} />
        )}

        {activeTab === 'settings' && (
          <SettingsPage />
        )}
      </main>

      {/* Evidence Drill-down Modal */}
      <EvidenceModal
        evidence={activeEvidence}
        onClose={() => setActiveEvidence(null)}
      />

      {/* Footer */}
      <footer className="bg-white border-t border-slate-200 py-4 no-print text-center text-xs text-slate-500 font-mono">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-2">
          <span>Consulting in a Box © 2024–2026 • Enterprise Decision Intelligence Engine</span>
          <span className="flex items-center space-x-1 text-slate-400">
            <span>Deterministic Analytics Engine</span>
            <span>•</span>
            <span className="text-emerald-600 font-medium">100% Audit Verified</span>
          </span>
        </div>
      </footer>

    </div>
  );
};

export default App;
