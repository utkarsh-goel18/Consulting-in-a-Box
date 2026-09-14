import React, { useState, useEffect } from 'react';
import { 
  Sliders, 
  RefreshCw, 
  ArrowRight, 
  TrendingUp, 
  CheckCircle2, 
  AlertCircle, 
  Sparkles, 
  RotateCcw,
  DollarSign
} from 'lucide-react';
import { ConsultingDashboard, ScenarioLevers, ScenarioResult } from '../types';
import { simulateScenario } from '../api/client';
import { 
  ResponsiveContainer, 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  Tooltip, 
  Cell, 
  CartesianGrid 
} from 'recharts';

interface ScenariosPageProps {
  data: ConsultingDashboard;
}

const DEFAULT_LEVERS: ScenarioLevers = {
  price_change_pct: 0.0,
  marketing_spend_delta_pct: 0.0,
  churn_rate_delta_pp: 0.0,
  delivery_cost_delta_pct: 0.0,
  cogs_reduction_pct: 0.0,
  return_rate_delta_pp: 0.0,
};

export const ScenariosPage: React.FC<ScenariosPageProps> = ({ data }) => {
  const [levers, setLevers] = useState<ScenarioLevers>(DEFAULT_LEVERS);
  const [result, setResult] = useState<ScenarioResult | null>(null);
  const [simulating, setSimulating] = useState<boolean>(false);

  const runSimulation = async (currentLevers: ScenarioLevers) => {
    try {
      setSimulating(true);
      const res = await simulateScenario(currentLevers);
      setResult(res);
    } catch (err) {
      console.error(err);
    } finally {
      setSimulating(false);
    }
  };

  useEffect(() => {
    runSimulation(levers);
  }, []);

  const handleLeverChange = (field: keyof ScenarioLevers, val: number) => {
    const updated = { ...levers, [field]: val };
    setLevers(updated);
    runSimulation(updated);
  };

  const applyPreset = (presetLevers: Partial<ScenarioLevers>) => {
    const updated = { ...DEFAULT_LEVERS, ...presetLevers };
    setLevers(updated);
    runSimulation(updated);
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-200">
      
      {/* Header */}
      <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-base font-bold text-slate-900 tracking-tight flex items-center space-x-2">
            <Sliders className="w-5 h-5 text-blue-600" />
            <span>What-If Scenario Simulator & Financial Sensitivity Engine</span>
          </h2>
          <p className="text-xs text-slate-500 mt-1">
            Simulate operational levers across pricing elasticity, logistics renegotiations, marketing spend, and churn mitigation.
          </p>
        </div>

        {/* Quick Presets */}
        <div className="flex flex-wrap items-center gap-2">
          <button
            onClick={() => applyPreset({ price_change_pct: 5.0, delivery_cost_delta_pct: -8.0, churn_rate_delta_pp: -2.0 })}
            className="px-3 py-1.5 bg-blue-50 hover:bg-blue-100 text-blue-700 text-xs font-semibold rounded-lg border border-blue-200 transition-colors"
          >
            Recommended Package (+5% Price, -8% Shipping)
          </button>
          <button
            onClick={() => applyPreset({ delivery_cost_delta_pct: -12.0, cogs_reduction_pct: -3.0, marketing_spend_delta_pct: -15.0 })}
            className="px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold rounded-lg transition-colors"
          >
            Aggressive Cost Containment
          </button>
          <button
            onClick={() => applyPreset(DEFAULT_LEVERS)}
            className="p-1.5 text-slate-400 hover:text-slate-600 rounded-lg hover:bg-slate-100 transition-colors"
            title="Reset to Base Case"
          >
            <RotateCcw className="w-4 h-4" />
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        
        {/* Left Column: Interactive Levers Sliders */}
        <div className="lg:col-span-5 bg-white p-5 rounded-xl border border-slate-200 shadow-sm space-y-5">
          <div className="pb-3 border-b border-slate-100 flex items-center justify-between">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700">
              Operational Decision Levers
            </h3>
            <span className="text-[11px] font-mono text-slate-400">Microeconomic Elasticity</span>
          </div>

          <div className="space-y-4 text-xs">
            {/* Lever 1: Price Change */}
            <div>
              <div className="flex justify-between font-semibold text-slate-800 mb-1">
                <span>Average Retail Price / AOV</span>
                <span className="font-mono text-blue-600 font-bold">
                  {levers.price_change_pct > 0 ? '+' : ''}{levers.price_change_pct}%
                </span>
              </div>
              <input
                type="range"
                min="-10"
                max="20"
                step="1"
                value={levers.price_change_pct}
                onChange={(e) => handleLeverChange('price_change_pct', parseFloat(e.target.value))}
                className="w-full h-1.5 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
              />
              <span className="text-[10px] text-slate-400">Elasticity modeled at -0.75</span>
            </div>

            {/* Lever 2: Delivery Cost per Order */}
            <div>
              <div className="flex justify-between font-semibold text-slate-800 mb-1">
                <span>Carrier Delivery Rate Optimization</span>
                <span className="font-mono text-blue-600 font-bold">
                  {levers.delivery_cost_delta_pct > 0 ? '+' : ''}{levers.delivery_cost_delta_pct}%
                </span>
              </div>
              <input
                type="range"
                min="-20"
                max="15"
                step="1"
                value={levers.delivery_cost_delta_pct}
                onChange={(e) => handleLeverChange('delivery_cost_delta_pct', parseFloat(e.target.value))}
                className="w-full h-1.5 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
              />
              <span className="text-[10px] text-slate-400">Vendor renegotiation and dynamic carrier routing</span>
            </div>

            {/* Lever 3: Customer Churn Improvement */}
            <div>
              <div className="flex justify-between font-semibold text-slate-800 mb-1">
                <span>Customer Churn Reduction</span>
                <span className="font-mono text-blue-600 font-bold">
                  {levers.churn_rate_delta_pp > 0 ? '+' : ''}{levers.churn_rate_delta_pp.toFixed(1)} pp
                </span>
              </div>
              <input
                type="range"
                min="-4"
                max="3"
                step="0.5"
                value={levers.churn_rate_delta_pp}
                onChange={(e) => handleLeverChange('churn_rate_delta_pp', parseFloat(e.target.value))}
                className="w-full h-1.5 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
              />
              <span className="text-[10px] text-slate-400">Removing regional delivery surcharges in Tier-2</span>
            </div>

            {/* Lever 4: Marketing Spend Budget Rebalancing */}
            <div>
              <div className="flex justify-between font-semibold text-slate-800 mb-1">
                <span>Marketing Spend Reallocation</span>
                <span className="font-mono text-blue-600 font-bold">
                  {levers.marketing_spend_delta_pct > 0 ? '+' : ''}{levers.marketing_spend_delta_pct}%
                </span>
              </div>
              <input
                type="range"
                min="-30"
                max="20"
                step="5"
                value={levers.marketing_spend_delta_pct}
                onChange={(e) => handleLeverChange('marketing_spend_delta_pct', parseFloat(e.target.value))}
                className="w-full h-1.5 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
              />
              <span className="text-[10px] text-slate-400">Scaling down Paid Social to expand Google Ads & Affiliate</span>
            </div>

            {/* Lever 5: COGS Sourcing Optimization */}
            <div>
              <div className="flex justify-between font-semibold text-slate-800 mb-1">
                <span>COGS Sourcing & Supplier Terms</span>
                <span className="font-mono text-blue-600 font-bold">
                  {levers.cogs_reduction_pct > 0 ? '+' : ''}{levers.cogs_reduction_pct}%
                </span>
              </div>
              <input
                type="range"
                min="-8"
                max="5"
                step="1"
                value={levers.cogs_reduction_pct}
                onChange={(e) => handleLeverChange('cogs_reduction_pct', parseFloat(e.target.value))}
                className="w-full h-1.5 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
              />
              <span className="text-[10px] text-slate-400">Bulk procurement renegotiation in Electronics</span>
            </div>
          </div>

          <div className="p-3 bg-slate-50 border border-slate-200 rounded-lg text-[11px] text-slate-500 leading-relaxed">
            <span className="font-bold text-slate-700 block mb-0.5">Statistical Sensitivity Notice:</span>
            Scenario modeling utilizes non-linear microeconomic elasticity functions. Outcomes are analytical estimates 
            conditioned on the explicit assumptions outlined on the right.
          </div>
        </div>

        {/* Right Column: Base Case vs Scenario Comparison */}
        <div className="lg:col-span-7 space-y-5">
          {/* Executive Verdict Callout */}
          {result && (
            <div className="bg-slate-900 text-white p-4 rounded-xl border border-slate-800 shadow-md">
              <div className="flex items-center space-x-2 text-blue-400 text-xs font-bold uppercase tracking-wider mb-1">
                <Sparkles className="w-4 h-4" />
                <span>Simulated Financial Impact</span>
              </div>
              <p className="text-xs text-slate-200 leading-relaxed font-sans">
                {result.executive_verdict}
              </p>
            </div>
          )}

          {/* Comparison Table */}
          {result && (
            <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm">
              <div className="flex items-center justify-between mb-3 pb-2 border-b border-slate-100">
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700">
                  Base Case vs Simulated Scenario
                </h3>
                <span className="text-[11px] font-mono text-slate-400">Quarterly Metrics</span>
              </div>

              <div className="border border-slate-200 rounded-lg overflow-hidden">
                <table className="min-w-full divide-y divide-slate-200 text-xs text-left">
                  <thead className="bg-slate-50 text-slate-600 font-semibold font-mono">
                    <tr>
                      <th className="px-4 py-2.5">Key Metric</th>
                      <th className="px-4 py-2.5">Base Case</th>
                      <th className="px-4 py-2.5">Simulated</th>
                      <th className="px-4 py-2.5">Net Variance</th>
                      <th className="px-4 py-2.5">Verdict</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-200 bg-white font-mono">
                    {Object.values(result.metrics).map((m) => (
                      <tr key={m.metric_name} className="hover:bg-slate-50 transition-colors">
                        <td className="px-4 py-2.5 font-sans font-bold text-slate-900">{m.metric_name}</td>
                        <td className="px-4 py-2.5 text-slate-600">{m.formatted_base}</td>
                        <td className="px-4 py-2.5 font-bold text-slate-900">{m.formatted_scenario}</td>
                        <td className={`px-4 py-2.5 font-semibold ${m.is_positive_trend ? 'text-emerald-700' : 'text-rose-700'}`}>
                          {m.formatted_delta}
                        </td>
                        <td className="px-4 py-2.5 font-sans">
                          <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                            m.is_positive_trend ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' : 'bg-rose-50 text-rose-700 border border-rose-200'
                          }`}>
                            {m.is_positive_trend ? 'Favorable' : 'Unfavorable'}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Key Assumptions & Disclaimers */}
          {result && (
            <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm">
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-700 mb-2">
                Explicit Governing Assumptions
              </h4>
              <ul className="space-y-1.5 text-xs text-slate-600 list-disc list-inside">
                {result.key_assumptions.map((assump, idx) => (
                  <li key={idx} className="leading-relaxed">{assump}</li>
                ))}
              </ul>
            </div>
          )}

        </div>

      </div>

    </div>
  );
};
