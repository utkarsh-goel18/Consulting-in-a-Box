import React, { useEffect, useState } from 'react';
import { Activity, ArrowRight, BarChart3, CheckCircle2, Compass, DollarSign, Package, Play, ShoppingBag, Sparkles, Target, TrendingDown, Users } from 'lucide-react';
import { AnalysisPlan, ConsultingCase } from '../types';
import { executeAnalysis, generateAnalysisPlan, getConsultingCases } from '../api/client';

interface Props { onPlanExecuted: () => void; }

const icons: Record<string, React.ReactNode> = {
  TrendingDown: <TrendingDown className="h-4 w-4" />, Users: <Users className="h-4 w-4" />, BarChart3: <BarChart3 className="h-4 w-4" />,
  DollarSign: <DollarSign className="h-4 w-4" />, Target: <Target className="h-4 w-4" />, ShoppingBag: <ShoppingBag className="h-4 w-4" />,
  Package: <Package className="h-4 w-4" />, Activity: <Activity className="h-4 w-4" />,
};

export const AnalysisPage: React.FC<Props> = ({ onPlanExecuted }) => {
  const [cases, setCases] = useState<ConsultingCase[]>([]);
  const [selectedCaseId, setSelectedCaseId] = useState('case_profitability_decline');
  const [customProblem, setCustomProblem] = useState('');
  const [plan, setPlan] = useState<AnalysisPlan | null>(null);
  const [execution, setExecution] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [executing, setExecuting] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    getConsultingCases().then(setCases).catch(err => setError(err.message));
    generateAnalysisPlan('case_profitability_decline').then(setPlan).catch(err => setError(err.message));
  }, []);

  const chooseCase = async (id: string) => {
    setSelectedCaseId(id); setCustomProblem(''); setExecution(null); setError(''); setLoading(true);
    try { setPlan(await generateAnalysisPlan(id)); } catch (err: any) { setError(err.message); } finally { setLoading(false); }
  };

  const submitCustom = async (event: React.FormEvent) => {
    event.preventDefault(); if (!customProblem.trim()) return;
    setSelectedCaseId('custom'); setExecution(null); setError(''); setLoading(true);
    try { setPlan(await generateAnalysisPlan('custom', customProblem)); } catch (err: any) { setError(err.message); } finally { setLoading(false); }
  };

  const run = async () => {
    if (!plan) return;
    setExecuting(true); setError('');
    try { setExecution(await executeAnalysis(selectedCaseId, customProblem)); } catch (err: any) { setError(err.message); } finally { setExecuting(false); }
  };

  return (
    <div className="space-y-6">
      <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-[0.16em] text-blue-600"><Compass className="h-4 w-4" /> Consulting workflow</div>
            <h1 className="mt-2 text-2xl font-bold tracking-tight text-slate-900 dark:text-white">Define the business problem. Then run the analysis.</h1>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-500">The AI layer structures the question; the deterministic analytics engine executes the numbers. This keeps narrative generation separate from calculation.</p>
          </div>
          <div className="rounded-xl border border-blue-100 bg-blue-50 px-4 py-3 text-xs text-blue-800 dark:border-blue-900/50 dark:bg-blue-950/30 dark:text-blue-200">8 standard cases · custom problem supported</div>
        </div>
      </section>

      {error && <div className="rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-xs text-rose-700">{error}</div>}

      <div className="grid gap-6 lg:grid-cols-[420px_1fr]">
        <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
          <div className="mb-4 text-xs font-bold uppercase tracking-wider text-slate-500">1 · Choose an engagement</div>
          <div className="space-y-2">
            {cases.map(c => {
              const selected = selectedCaseId === c.id;
              return <button key={c.id} onClick={() => chooseCase(c.id)} className={`flex w-full items-start gap-3 rounded-xl border p-3 text-left transition ${selected ? 'border-blue-400 bg-blue-50 dark:border-blue-700 dark:bg-blue-950/30' : 'border-slate-200 hover:border-slate-300 hover:bg-slate-50 dark:border-slate-800 dark:hover:bg-slate-950'}`}>
                <span className={`mt-0.5 rounded-lg p-2 ${selected ? 'bg-blue-600 text-white' : 'bg-slate-100 text-slate-500 dark:bg-slate-800'}`}>{icons[c.icon] || icons.Activity}</span>
                <span className="min-w-0 flex-1"><span className="flex items-center justify-between gap-2"><span className="text-xs font-bold text-slate-900 dark:text-white">{c.title}</span><span className="text-[10px] text-slate-400">{c.category}</span></span><span className="mt-1 block text-[11px] leading-5 text-slate-500">{c.default_question}</span></span>
              </button>;
            })}
          </div>
          <form onSubmit={submitCustom} className="mt-5 border-t border-slate-100 pt-5 dark:border-slate-800">
            <div className="mb-2 flex items-center gap-2 text-xs font-bold text-slate-700 dark:text-slate-200"><Sparkles className="h-4 w-4 text-blue-500" /> Custom business problem</div>
            <textarea value={customProblem} onChange={e => setCustomProblem(e.target.value)} rows={4} placeholder="e.g. Why did contribution margin deteriorate in the latest quarter?" className="w-full resize-none rounded-xl border border-slate-200 bg-slate-50 p-3 text-xs outline-none focus:border-blue-400 focus:ring-2 focus:ring-blue-100 dark:border-slate-800 dark:bg-slate-950" />
            <button disabled={!customProblem.trim() || loading} className="mt-2 flex w-full items-center justify-center gap-2 rounded-xl bg-slate-900 px-4 py-2.5 text-xs font-semibold text-white disabled:opacity-40"><Sparkles className="h-3.5 w-3.5" /> Generate custom plan</button>
          </form>
        </section>

        <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
          <div className="mb-5 flex flex-col gap-4 border-b border-slate-100 pb-5 sm:flex-row sm:items-start sm:justify-between dark:border-slate-800">
            <div><div className="text-[10px] font-bold uppercase tracking-wider text-blue-600">2 · Generated analysis plan</div><h2 className="mt-1 text-lg font-bold text-slate-900 dark:text-white">{loading ? 'Building plan…' : plan?.case_title || 'Select a case'}</h2><p className="mt-1 text-xs leading-5 text-slate-500">{plan?.business_question}</p></div>
            <button onClick={run} disabled={!plan || executing || loading} className="inline-flex shrink-0 items-center justify-center gap-2 rounded-xl bg-blue-600 px-4 py-2.5 text-xs font-semibold text-white shadow-sm hover:bg-blue-500 disabled:opacity-40"><Play className="h-3.5 w-3.5 fill-current" /> {executing ? 'Executing…' : 'Execute analysis'}</button>
          </div>

          {!plan && !loading && <div className="py-16 text-center text-sm text-slate-400">Choose a consulting case to generate an analytical workplan.</div>}
          {loading && <div className="py-16 text-center text-sm text-slate-400">Structuring the problem and selecting analytical methods…</div>}
          {plan && !loading && <div className="space-y-3">
            {plan.steps.map(step => <div key={step.step_number} className="rounded-xl border border-slate-200 p-4 dark:border-slate-800"><div className="flex items-center gap-3"><span className="flex h-7 w-7 items-center justify-center rounded-full bg-blue-50 text-xs font-bold text-blue-700 dark:bg-blue-950/40 dark:text-blue-300">{step.step_number}</span><div className="flex-1"><div className="flex flex-wrap items-center gap-2"><span className="text-xs font-bold text-slate-900 dark:text-white">{step.title}</span><span className="rounded bg-slate-100 px-2 py-1 font-mono text-[10px] text-slate-500 dark:bg-slate-800">{step.method}</span></div><p className="mt-1 text-xs leading-5 text-slate-500">{step.description}</p></div></div><div className="mt-3 flex flex-wrap gap-1.5 pl-10">{step.target_metrics.map(metric => <span key={metric} className="rounded-md bg-blue-50 px-2 py-1 font-mono text-[10px] text-blue-700 dark:bg-blue-950/40 dark:text-blue-300">{metric}</span>)}</div></div>)}
            <div className="flex items-start gap-2 rounded-xl border border-emerald-200 bg-emerald-50 p-3 text-xs text-emerald-800 dark:border-emerald-900/50 dark:bg-emerald-950/20 dark:text-emerald-300"><CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0" /><span>Governance: numerical results come from deterministic SQL/Pandas calculations. AI is used for plan structure and interpretation, not arithmetic.</span></div>
          </div>}

          {execution && <div className="mt-6 border-t border-slate-100 pt-5 dark:border-slate-800"><div className="mb-3 text-xs font-bold uppercase tracking-wider text-slate-500">3 · Execution audit</div><div className="space-y-2">{execution.timeline.map((item: any) => <div key={item.step} className="flex gap-3 rounded-lg bg-slate-50 p-3 dark:bg-slate-950"><CheckCircle2 className="h-4 w-4 shrink-0 text-emerald-500" /><div><div className="text-xs font-semibold text-slate-800 dark:text-slate-100">{item.title}</div><div className="text-[11px] text-slate-500">{item.detail}</div></div></div>)}</div><button onClick={onPlanExecuted} className="mt-4 inline-flex items-center gap-2 text-xs font-semibold text-blue-600 hover:underline">Open verified insights <ArrowRight className="h-3.5 w-3.5" /></button></div>}
        </section>
      </div>
    </div>
  );
};
