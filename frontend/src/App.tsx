import React, { useEffect, useState } from 'react';
import { Navbar } from './components/layout/Navbar';
import { DashboardPageINR as DashboardPage } from './pages/DashboardPageINR';
import { DatasetsPageV2 as DatasetsPage } from './pages/DatasetsPageV2';
import { AnalysisPage } from './pages/AnalysisPage';
import { InsightsPage } from './pages/InsightsPage';
import { ScenariosPage } from './pages/ScenariosPage';
import { ReportsPage } from './pages/ReportsPage';
import { SettingsPage } from './pages/SettingsPage';
import { EvidenceModal } from './components/common/EvidenceModal';
import { ConsultingDashboard, EvidenceDetail } from './types';
import { bootstrapDemo, getEvidenceDetail } from './api/client';
import { Loader2, RefreshCw } from 'lucide-react';
import { Logo } from './components/brand/Logo';

const CACHE_KEY = 'cib-dashboard-v3';

export const App: React.FC = () => {
  const cached = (() => { try { return JSON.parse(sessionStorage.getItem(CACHE_KEY) || 'null') as ConsultingDashboard | null; } catch { return null; } })();
  const [activeTab, setActiveTab] = useState('dashboard');
  const [dashboardData, setDashboardData] = useState<ConsultingDashboard | null>(cached);
  const [loading, setLoading] = useState(!cached);
  const [demoLoading, setDemoLoading] = useState(false);
  const [demoProgressStep, setDemoProgressStep] = useState('');
  const [activeEvidence, setActiveEvidence] = useState<EvidenceDetail | null>(null);
  const [loadError, setLoadError] = useState('');
  const [darkMode, setDarkMode] = useState(() => localStorage.getItem('cib-theme') === 'dark');

  useEffect(() => { document.documentElement.classList.toggle('dark', darkMode); localStorage.setItem('cib-theme', darkMode ? 'dark' : 'light'); }, [darkMode]);
  const loadDashboard = async (force = false) => {
    try { setLoadError(''); if (force) setDemoLoading(true); setDemoProgressStep('Refreshing deterministic decision data…'); const data = await bootstrapDemo(); setDashboardData(data); sessionStorage.setItem(CACHE_KEY, JSON.stringify(data)); setActiveTab('dashboard'); }
    catch (err: any) { setLoadError(err?.message || 'Unable to connect to the analytical engine.'); }
    finally { setLoading(false); setDemoLoading(false); setDemoProgressStep(''); }
  };
  useEffect(() => { loadDashboard(false); }, []);
  const handleOpenEvidence = async (evidenceId: string) => { try { setActiveEvidence(await getEvidenceDetail(evidenceId)); } catch (err: any) { alert(`Failed to load evidence audit: ${err.message}`); } };

  return <div className={`min-h-screen font-sans transition-colors duration-200 ${darkMode ? 'dark bg-[#0b1120] text-slate-100' : 'bg-[#f6f8fb] text-slate-900'}`}>
    <Navbar activeTab={activeTab} setActiveTab={setActiveTab} onRunDemo={() => loadDashboard(true)} demoLoading={demoLoading} demoProgressStep={demoProgressStep} darkMode={darkMode} onToggleTheme={() => setDarkMode(value => !value)} />
    <main className="mx-auto w-full max-w-[1440px] px-4 py-6 sm:px-6 lg:px-8 lg:py-8">
      {loading && !dashboardData && <div className="flex min-h-[60vh] items-center justify-center"><div className="w-full max-w-md rounded-3xl border border-slate-200 bg-white p-8 text-center shadow-sm dark:border-slate-800 dark:bg-slate-900"><div className="mx-auto mb-5 flex justify-center"><Logo size={48} compact /></div><h1 className="text-base font-bold text-slate-900 dark:text-white">Preparing the decision workspace</h1><p className="mt-2 text-sm text-slate-500">Loading the deterministic NovaMart snapshot.</p><div className="mt-6 flex items-center justify-center gap-2 text-xs text-slate-400"><Loader2 className="h-4 w-4 animate-spin" /> Analytical engine loading…</div></div></div>}
      {loadError && !dashboardData && <div className="flex min-h-[60vh] items-center justify-center"><div className="max-w-md rounded-3xl border border-rose-200 bg-white p-8 text-center shadow-sm dark:border-rose-900 dark:bg-slate-900"><h2 className="font-bold text-slate-900 dark:text-white">Decision engine unavailable</h2><p className="mt-2 text-sm text-slate-500">{loadError}</p><button onClick={() => loadDashboard(true)} className="mt-5 inline-flex items-center gap-2 rounded-xl bg-slate-900 px-4 py-2.5 text-sm font-semibold text-white"><RefreshCw className="h-4 w-4" /> Retry</button></div></div>}
      {dashboardData && activeTab === 'dashboard' && <DashboardPage data={dashboardData} onNavigate={setActiveTab} onViewEvidence={handleOpenEvidence} />}
      {activeTab === 'datasets' && <DatasetsPage />}
      {activeTab === 'analysis' && <AnalysisPage onPlanExecuted={() => setActiveTab('insights')} />}
      {activeTab === 'insights' && dashboardData && <InsightsPage data={dashboardData} onViewEvidence={handleOpenEvidence} />}
      {activeTab === 'scenarios' && dashboardData && <ScenariosPage data={dashboardData} />}
      {activeTab === 'reports' && dashboardData && <ReportsPage dashboardData={dashboardData} />}
      {activeTab === 'settings' && <SettingsPage />}
    </main>
    <EvidenceModal evidence={activeEvidence} onClose={() => setActiveEvidence(null)} />
    <footer className="border-t border-slate-200 bg-white dark:border-slate-800 dark:bg-[#0f172a]"><div className="mx-auto flex max-w-[1440px] flex-col gap-2 px-4 py-4 text-[11px] text-slate-400 sm:flex-row sm:items-center sm:justify-between sm:px-6 lg:px-8"><span className="flex items-center gap-2"><Logo size={18} compact /> Consulting in a Box · Enterprise Decision Intelligence</span><span>INR reporting · Deterministic analytics · Audit-ready evidence</span></div></footer>
  </div>;
};
export default App;
