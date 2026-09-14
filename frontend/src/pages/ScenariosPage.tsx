import React, { useEffect, useState } from 'react';
import { RotateCcw, Sliders, Sparkles, Target } from 'lucide-react';
import { ConsultingDashboard, ScenarioLevers, ScenarioResult } from '../types';
import { simulateScenario } from '../api/client';

interface Props { data: ConsultingDashboard; }

const DEFAULT_LEVERS: ScenarioLevers = { price_change_pct: 0, marketing_spend_delta_pct: 0, churn_rate_delta_pp: 0, delivery_cost_delta_pct: 0, cogs_reduction_pct: 0, return_rate_delta_pp: 0 };
const leverMeta: Array<{ key: keyof ScenarioLevers; label: string; min: number; max: number; step: number; suffix: string }> = [
  { key: 'price_change_pct', label: 'Price / AOV', min: -10, max: 20, step: 1, suffix: '%' },
  { key: 'marketing_spend_delta_pct', label: 'Marketing spend', min: -30, max: 20, step: 5, suffix: '%' },
  { key: 'churn_rate_delta_pp', label: 'Churn rate', min: -4, max: 3, step: 0.5, suffix: ' pp' },
  { key: 'delivery_cost_delta_pct', label: 'Delivery cost', min: -20, max: 15, step: 1, suffix: '%' },
  { key: 'cogs_reduction_pct', label: 'COGS', min: -8, max: 5, step: 1, suffix: '%' },
  { key: 'return_rate_delta_pp', label: 'Return rate', min: -3, max: 3, step: 0.5, suffix: ' pp' },
];

export const ScenariosPage: React.FC<Props> = ({ data }) => {
  const [levers, setLevers] = useState(DEFAULT_LEVERS);
  const [result, setResult] = useState<ScenarioResult | null>(null);
  const [busy, setBusy] = useState(false);

  const run = async (next: ScenarioLevers) => {
    setBusy(true);
    try { setResult(await simulateScenario(next)); } finally { setBusy(false); }
  };
  useEffect(() => { run(DEFAULT_LEVERS); }, []);
  const update = (key: keyof ScenarioLevers, value: number) => { const next = { ...levers, [key]: value }; setLevers(next); run(next); };

  return (
    <div className="space-y-6 animate-in fade-in duration-200">
      <header className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-[0.16em] text-blue-600"><Sliders className="h-4 w-4" /> Decision simulator</div>
            <h1 className="mt-2 text-2xl font-bold tracking-tight text-slate-900 dark:text-white">What changes if we pull these levers?</h1>
            <p className="mt-2 max-w-3xl text-sm text-slate-500">Run transparent sensitivity scenarios against the verified {data.company_name} base case. Every result is a modeled estimate, not a forecast.</p>
          </div>
          <div className="flex gap-2">
            <button onClick={() => { setLevers(DEFAULT_LEVERS); run(DEFAULT_LEVERS); }} className="inline-flex items-center gap-2 rounded-xl border border-slate-200 px-3 py-2 text-xs font-semibold text-slate-700 hover:bg-slate-50"><RotateCcw className="h-4 w-4" /> Reset</button>
            <button onClick={() => { const next = { ...DEFAULT_LEVERS, price_change_pct: 5, delivery_cost_delta_pct: -8, churn_rate_delta_pp: -2 }; setLevers(next); run(next); }} className="inline-flex items-center gap-2 rounded-xl bg-slate-900 px-3 py-2 text-xs font-semibold text-white"><Target className="h-4 w-4" /> Recommended case</button>
          </div>
        </div>
      </header>

      <div className="grid gap-6 lg:grid-cols-[420px_1fr]">
        <section className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
          <div className="mb-5 flex items-center justify-between"><h2 className="text-sm font-bold text-slate-900 dark:text-white">Decision levers</h2><span className="text-[11px] text-slate-400">Deterministic model</span></div>
          <div className="space-y-6">
            {leverMeta.map(meta => {
              const value = levers[meta.key] as number;
              return <div key={meta.key}>
                <div className="mb-2 flex items-center justify-between"><label className="text-xs font-semibold text-slate-700 dark:text-slate-200">{meta.label}</label><span className="font-mono text-xs font-bold text-blue-600">{value > 0 ? '+' : ''}{value}{meta.suffix}</span></div>
                <input aria-label={meta.label} type="range" min={meta.min} max={meta.max} step={meta.step} value={value} onChange={e => update(meta.key, Number(e.target.value))} className="w-full accent-blue-600" />
                <div className="mt-1 flex justify-between text-[10px] text-slate-400"><span>{meta.min}{meta.suffix}</span><span>{meta.max}{meta.suffix}</span></div>
              </div>;
            })}
          </div>
        </section>

        <section className="space-y-6">
          <div className="rounded-3xl bg-slate-950 p-6 text-white shadow-sm">
            <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-[0.16em] text-blue-400"><Sparkles className="h-4 w-4" /> Simulated outcome</div>
            <p className="mt-3 text-sm leading-7 text-slate-200">{busy ? 'Recalculating the scenario…' : result?.executive_verdict}</p>
          </div>

          {result && <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
            <div className="mb-4"><h2 className="text-sm font-bold text-slate-900 dark:text-white">Baseline vs scenario</h2><p className="mt-1 text-xs text-slate-500">Positive / negative status is metric-aware: higher profit is good, higher CAC is not.</p></div>
            <div className="overflow-x-auto rounded-2xl border border-slate-200 dark:border-slate-800">
              <table className="min-w-full text-left text-xs"><thead className="bg-slate-50 dark:bg-slate-950"><tr><th className="px-4 py-3">Metric</th><th className="px-4 py-3">Base</th><th className="px-4 py-3">Scenario</th><th className="px-4 py-3">Delta</th><th className="px-4 py-3">Signal</th></tr></thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800">{Object.values(result.metrics).map(m => <tr key={m.metric_name}><td className="px-4 py-3 font-semibold text-slate-800 dark:text-slate-100">{m.metric_name}</td><td className="px-4 py-3 font-mono text-slate-500">{m.formatted_base}</td><td className="px-4 py-3 font-mono font-semibold text-slate-800 dark:text-slate-100">{m.formatted_scenario}</td><td className={`px-4 py-3 font-mono font-semibold ${m.is_positive_trend ? 'text-emerald-600' : 'text-rose-600'}`}>{m.formatted_delta}</td><td className="px-4 py-3">{m.is_positive_trend ? 'Favorable' : 'Unfavorable'}</td></tr>)}</tbody></table>
            </div>
          </div>}

          {result && <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
            <h2 className="text-sm font-bold text-slate-900 dark:text-white">Scenario profit bridge</h2>
            <div className="mt-4 grid gap-2 sm:grid-cols-2 lg:grid-cols-3">{result.waterfall_breakdown.map((item, i) => <div key={i} className="rounded-2xl border border-slate-100 bg-slate-50 p-4 dark:border-slate-800 dark:bg-slate-950"><div className="text-[11px] font-semibold text-slate-500">{item.lever}</div><div className="mt-1 font-mono text-sm font-bold text-slate-900 dark:text-white">₹{Number(item.amount).toLocaleString('en-IN')}</div></div>)}</div>
            <div className="mt-5 border-t border-slate-100 pt-4 dark:border-slate-800"><h3 className="text-xs font-bold text-slate-700 dark:text-slate-200">Governing assumptions</h3><ul className="mt-2 grid gap-2 text-xs text-slate-500 md:grid-cols-2">{result.key_assumptions.map((x, i) => <li key={i}>• {x}</li>)}</ul></div>
          </div>}
        </section>
      </div>
    </div>
  );
};
