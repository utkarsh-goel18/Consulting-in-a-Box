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
import { ArrowRight, BarChart3, Database, FileText, Loader2, RefreshCw, ShieldCheck, Sparkles, TrendingUp } from 'lucide-react';
import { Logo } from './components/brand/Logo';

const CACHE_KEY = 'cib-dashboard-v5-runtime-validation';
const DEMO_STARTED_KEY = 'cib-demo-engagement-started-v2';
const ANALYSIS_DASHBOARD_KEY = 'cib-analysis-dashboard-v1';

const isFiniteNumber = (value: unknown): value is number => typeof value === 'number' && Number.isFinite(value);

const isUsableDashboard = (value: unknown): value is ConsultingDashboard => {
  if (!value || typeof value !== 'object') return false;
  const data = value as Partial<ConsultingDashboard>;
  const kpi = data.kpi_summary as Partial<ConsultingDashboard['kpi_summary']> | undefined;
  if (!kpi || !data.driver_tree || !Array.isArray(data.p_and_l_waterfall)) return false;
  const requiredKpis = [
    kpi.revenue_prior, kpi.revenue_current, kpi.revenue_growth_pct,
    kpi.gross_profit_prior, kpi.gross_profit_current, kpi.gross_profit_growth_pct,
    kpi.net_profit_prior, kpi.net_profit_current, kpi.net_profit_growth_pct,
    kpi.net_margin_prior_pct, kpi.net_margin_current_pct, kpi.net_margin_delta_pp,
    kpi.orders_prior, kpi.orders_current, kpi.orders_growth_pct,
    kpi.aov_prior, kpi.aov_current, kpi.aov_growth_pct,
    kpi.cac_prior, kpi.cac_current, kpi.cac_growth_pct,
    kpi.churn_rate_prior_pct, kpi.churn_rate_current_pct, kpi.churn_rate_delta_pp,
  ];
  return requiredKpis.every(isFiniteNumber) && data.p_and_l_waterfall.every(row =>
    row && typeof row.step === 'string' && isFiniteNumber(row.amount) && isFiniteNumber(row.running_total) && typeof row.type === 'string'
  );
};

const readCachedDashboard = (): ConsultingDashboard | null => {
  if (sessionStorage.getItem(DEMO_STARTED_KEY) !== 'true') return null;
  try {
    const parsed = JSON.parse(sessionStorage.getItem(CACHE_KEY) || 'null');
    return isUsableDashboard(parsed) ? parsed : null;
  } catch {
    return null;
  }
};

export const App: React.FC = () => {
  const cached = readCachedDashboard();
  const [activeTab, setActiveTab] = useState('dashboard');
  const [dashboardData, setDashboardData] = useState<ConsultingDashboard | null>(cached);
  const [demoLoading, setDemoLoading] = useState(false);
  const [demoProgressStep, setDemoProgressStep] = useState('');
  const [activeEvidence, setActiveEvidence] = useState<EvidenceDetail | null>(null);
  const [loadError, setLoadError] = useState('');
  const [darkMode, setDarkMode] = useState(() => localStorage.getItem('cib-theme') === 'dark');

  useEffect(() => { document.documentElement.classList.toggle('dark', darkMode); localStorage.setItem('cib-theme', darkMode ? 'dark' : 'light'); }, [darkMode]);

  const runDemo = async () => {
    try {
      setLoadError('');
      setDemoLoading(true);
      setDemoProgressStep('Preparing the NovaMart case…');
      const data = await bootstrapDemo();
      if (!isUsableDashboard(data)) throw new Error('The analytical engine returned an incomplete dashboard. Please restart the backend and try again.');
      setDemoProgressStep('Building the decision workspace…');
      setDashboardData(data);
      sessionStorage.setItem(CACHE_KEY, JSON.stringify(data));
      sessionStorage.setItem(DEMO_STARTED_KEY, 'true');
      setActiveTab('dashboard');
    } catch (err: any) {
      setLoadError(err?.message || 'Unable to connect to the analytical engine.');
    } finally {
      setDemoLoading(false);
      setDemoProgressStep('');
    }
  };

  const handleAnalysisExecuted = () => {
    try {
      const raw = sessionStorage.getItem(ANALYSIS_DASHBOARD_KEY);
      if (raw) {
        const data = JSON.parse(raw) as ConsultingDashboard;
        if (isUsableDashboard(data)) {
          setDashboardData(data);
          sessionStorage.setItem(CACHE_KEY, JSON.stringify(data));
          sessionStorage.setItem(DEMO_STARTED_KEY, 'true');
        }
      }
    } catch { /* keep the current workspace if the persisted result is malformed */ }
    setActiveTab('insights');
  };

  const handleOpenEvidence = async (evidenceId: string) => { try { setActiveEvidence(await getEvidenceDetail(evidenceId)); } catch (err: any) { alert(`Failed to load evidence audit: ${err.message}`); } };
  const showWorkspace = Boolean(dashboardData);

  return <div className={`min-h-screen font-sans transition-colors duration-200 ${darkMode ? 'dark bg-[#0b1120] text-slate-100' : 'bg-[#f6f8fb] text-slate-900'}`}>
    <Navbar activeTab={activeTab} setActiveTab={setActiveTab} onRunDemo={runDemo} demoLoading={demoLoading} demoProgressStep={demoProgressStep} darkMode={darkMode} onToggleTheme={() => setDarkMode(value => !value)} />
    <main className="mx-auto w-full max-w-[1440px] px-4 py-6 sm:px-6 lg:px-8 lg:py-8">
      {!showWorkspace && !demoLoading && !loadError && <section className="animate-in flex min-h-[calc(100vh-180px)] items-center justify-center py-8"><div className="w-full max-w-5xl"><div className="mx-auto max-w-3xl text-center"><div className="mx-auto mb-6 flex h-16 w-16 items-center justify-center rounded-2xl bg-slate-950 text-white shadow-xl dark:bg-white dark:text-slate-950"><Logo size={42} compact /></div><div className="mb-4 inline-flex items-center gap-2 rounded-full border border-blue-200 bg-blue-50 px-3 py-1.5 text-[11px] font-bold uppercase tracking-[0.16em] text-blue-700 dark:border-blue-900 dark:bg-blue-950/40 dark:text-blue-300"><Sparkles className="h-3.5 w-3.5" /> Interactive demo engagement</div><h1 className="text-4xl font-black tracking-tight text-slate-950 dark:text-white sm:text-5xl">From messy business data to a decision-ready answer.</h1><p className="mx-auto mt-5 max-w-2xl text-base leading-7 text-slate-500 dark:text-slate-400 sm:text-lg">See Consulting in a Box run a realistic NovaMart profitability case — from data and KPIs to driver diagnosis, recommendations, scenarios, and an executive report.</p><button onClick={runDemo} className="mt-8 inline-flex items-center gap-2 rounded-xl bg-blue-600 px-6 py-3.5 text-sm font-bold text-white shadow-lg shadow-blue-600/20 transition hover:bg-blue-700">Run Demo Engagement <ArrowRight className="h-4 w-4" /></button></div><div className="mx-auto mt-14 grid max-w-4xl gap-3 sm:grid-cols-4">{[{ icon: Database, title: 'Ingest', text: 'Structured business data' }, { icon: BarChart3, title: 'Analyze', text: 'Deterministic KPI engine' }, { icon: TrendingUp, title: 'Diagnose', text: 'Drivers & evidence' }, { icon: FileText, title: 'Decide', text: 'Actions & scenarios' }].map(({ icon: Icon, title, text }) => <div key={title} className="rounded-2xl border border-slate-200 bg-white/80 p-4 text-center shadow-sm dark:border-slate-800 dark:bg-slate-900/70"><Icon className="mx-auto h-5 w-5 text-blue-600" /><div className="mt-2 text-xs font-bold text-slate-800 dark:text-slate-100">{title}</div><div className="mt-1 text-[11px] text-slate-400">{text}</div></div>)}</div><div className="mx-auto mt-5 flex max-w-4xl items-center justify-center gap-2 text-[11px] text-slate-400"><ShieldCheck className="h-3.5 w-3.5" /> Deterministic calculations · Evidence-backed insights · INR reporting</div></div></section>}
      {demoLoading && !showWorkspace && <div className="flex min-h-[60vh] items-center justify-center"><div className="w-full max-w-lg rounded-3xl border border-slate-200 bg-white p-9 text-center shadow-sm dark:border-slate-800 dark:bg-slate-900"><div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-blue-50 dark:bg-blue-950/40"><Loader2 className="h-7 w-7 animate-spin text-blue-600" /></div><h1 className="mt-5 text-lg font-bold text-slate-900 dark:text-white">Running the demo engagement</h1><p className="mt-2 text-sm text-slate-500 dark:text-slate-400">{demoProgressStep || 'Running deterministic analysis…'}</p><div className="mx-auto mt-6 h-1.5 max-w-sm overflow-hidden rounded-full bg-slate-100 dark:bg-slate-800"><div className="h-full w-2/3 animate-pulse rounded-full bg-blue-600" /></div><div className="mt-5 grid grid-cols-4 gap-2 text-[10px] font-semibold text-slate-400"><span>Data</span><span>KPIs</span><span>Drivers</span><span>Decisions</span></div></div></div>}
      {loadError && !showWorkspace && !demoLoading && <div className="flex min-h-[60vh] items-center justify-center"><div className="max-w-md rounded-3xl border border-rose-200 bg-white p-8 text-center shadow-sm dark:border-rose-900 dark:bg-slate-900"><h2 className="font-bold text-slate-900 dark:text-white">Demo engagement unavailable</h2><p className="mt-2 text-sm text-slate-500 dark:text-slate-400">{loadError}</p><button onClick={runDemo} className="mt-5 inline-flex items-center gap-2 rounded-xl bg-slate-900 px-4 py-2.5 text-sm font-semibold text-white"><RefreshCw className="h-4 w-4" /> Try again</button></div></div>}
      {showWorkspace && activeTab === 'dashboard' && <DashboardPage data={dashboardData!} onNavigate={setActiveTab} onViewEvidence={handleOpenEvidence} />}
      {activeTab === 'datasets' && <DatasetsPage />}
      {activeTab === 'analysis' && <AnalysisPage onPlanExecuted={handleAnalysisExecuted} />}
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