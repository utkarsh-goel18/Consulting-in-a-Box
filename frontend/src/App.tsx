import React, { useEffect, useState } from 'react';
import { Navbar } from './components/layout/Navbar';
import { DashboardPageINR as DashboardPage } from './pages/DashboardPageINR';
import { DatasetsPage } from './pages/DatasetsPage';
import { AnalysisPage } from './pages/AnalysisPage';
import { InsightsPage } from './pages/InsightsPage';
import { ScenariosPage } from './pages/ScenariosPage';
import { ReportsPage } from './pages/ReportsPage';
import { SettingsPage } from './pages/SettingsPage';
import { EvidenceModal } from './components/common/EvidenceModal';
import { ConsultingDashboard, EvidenceDetail } from './types';
import { bootstrapDemo, getEvidenceDetail } from './api/client';
import { Loader2 } from 'lucide-react';
import { Logo } from './components/brand/Logo';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [dashboardData, setDashboardData] = useState<ConsultingDashboard | null>(null);
  const [loading, setLoading] = useState(true);
  const [demoLoading, setDemoLoading] = useState(false);
  const [demoProgressStep, setDemoProgressStep] = useState('');
  const [activeEvidence, setActiveEvidence] = useState<EvidenceDetail | null>(null);
  const [darkMode, setDarkMode] = useState(() => localStorage.getItem('cib-theme') === 'dark');

  useEffect(() => {
    document.documentElement.classList.toggle('dark', darkMode);
    localStorage.setItem('cib-theme', darkMode ? 'dark' : 'light');
  }, [darkMode]);

  const handleRunDemo = async () => {
    try {
      setDemoLoading(true);
      setDemoProgressStep('Loading decision workspace…');
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
    bootstrapDemo()
      .then(setDashboardData)
      .catch(err => console.error('Initial demo load failed:', err))
      .finally(() => setLoading(false));
  }, []);

  const handleOpenEvidence = async (evidenceId: string) => {
    try {
      setActiveEvidence(await getEvidenceDetail(evidenceId));
    } catch (err: any) {
      alert(`Failed to load evidence audit: ${err.message}`);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#07111f] text-white flex items-center justify-center px-6">
        <div className="w-full max-w-sm text-center">
          <div className="mx-auto mb-7 flex justify-center text-white"><Logo size={58} compact /></div>
          <div className="text-sm font-semibold tracking-wide text-white">Consulting in a Box</div>
          <div className="mt-2 flex items-center justify-center gap-2 text-xs text-slate-400">
            <Loader2 className="h-4 w-4 animate-spin" />
            <span>Preparing your decision workspace…</span>
          </div>
          <div className="mt-7 h-1 overflow-hidden rounded-full bg-white/10">
            <div className="h-full w-1/2 animate-pulse rounded-full bg-blue-500" />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`min-h-screen font-sans transition-colors duration-200 ${darkMode ? 'dark bg-[#0b1120] text-slate-100' : 'bg-[#f6f8fb] text-slate-900'}`}>
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        onRunDemo={handleRunDemo}
        demoLoading={demoLoading}
        demoProgressStep={demoProgressStep}
        darkMode={darkMode}
        onToggleTheme={() => setDarkMode(value => !value)}
      />

      <main className="mx-auto w-full max-w-[1440px] px-4 py-6 sm:px-6 lg:px-8 lg:py-8">
        {activeTab === 'dashboard' && dashboardData && <DashboardPage data={dashboardData} onNavigate={setActiveTab} onViewEvidence={handleOpenEvidence} />}
        {activeTab === 'datasets' && <DatasetsPage />}
        {activeTab === 'analysis' && <AnalysisPage onPlanExecuted={() => setActiveTab('insights')} />}
        {activeTab === 'insights' && dashboardData && <InsightsPage data={dashboardData} onViewEvidence={handleOpenEvidence} />}
        {activeTab === 'scenarios' && dashboardData && <ScenariosPage data={dashboardData} />}
        {activeTab === 'reports' && dashboardData && <ReportsPage dashboardData={dashboardData} />}
        {activeTab === 'settings' && <SettingsPage />}
      </main>

      <EvidenceModal evidence={activeEvidence} onClose={() => setActiveEvidence(null)} />

      <footer className="border-t border-slate-200 bg-white dark:border-slate-800 dark:bg-[#0f172a]">
        <div className="mx-auto flex max-w-[1440px] flex-col gap-2 px-4 py-4 text-[11px] text-slate-400 sm:flex-row sm:items-center sm:justify-between sm:px-6 lg:px-8">
          <span className="flex items-center gap-2"><Logo size={18} compact /> Consulting in a Box · Enterprise Decision Intelligence</span>
          <span>INR reporting · Deterministic analytics · Audit-ready evidence</span>
        </div>
      </footer>
    </div>
  );
};
export default App;
