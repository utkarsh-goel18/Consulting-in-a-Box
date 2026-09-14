import React, { useState } from 'react';
import { 
  TrendingDown, 
  TrendingUp, 
  DollarSign, 
  ShoppingCart, 
  Users, 
  Activity, 
  AlertTriangle, 
  ArrowRight, 
  ShieldCheck, 
  BarChart3, 
  Truck, 
  Layers 
} from 'lucide-react';
import { ConsultingDashboard } from '../types';
import { MetricCard } from '../components/common/MetricCard';
import { WaterfallChart } from '../components/charts/WaterfallChart';
import { 
  ResponsiveContainer, 
  LineChart, 
  Line, 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  Tooltip, 
  CartesianGrid 
} from 'recharts';

interface DashboardPageProps {
  data: ConsultingDashboard;
  onNavigate: (tab: string) => void;
  onViewEvidence: (evidenceId: string) => void;
}

export const DashboardPage: React.FC<DashboardPageProps> = ({
  data,
  onNavigate,
  onViewEvidence,
}) => {
  const [activeSubView, setActiveSubView] = useState<'waterfall' | 'trends' | 'carriers' | 'categories'>('waterfall');
  const kpi = data.kpi_summary;

  return (
    <div className="space-y-6 animate-in fade-in duration-200">
      
      {/* Executive Alert Banner */}
      <div className="bg-slate-900 text-white rounded-xl p-5 border border-slate-800 shadow-md">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex items-start space-x-4">
            <div className="p-2.5 bg-rose-500/20 text-rose-400 rounded-lg border border-rose-500/30 mt-0.5">
              <AlertTriangle className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="text-xs font-bold uppercase tracking-wider text-rose-400">
                  Critical Finding: {data.problem_title}
                </span>
                <span className="text-[10px] bg-slate-800 text-slate-300 px-2 py-0.5 rounded border border-slate-700">
                  {data.quarter_evaluated}
                </span>
              </div>
              <h2 className="text-lg font-bold tracking-tight text-white mt-1">
                Net Operating Profit contracted {Math.abs(kpi.net_profit_growth_pct).toFixed(1)}% QoQ (-${(kpi.net_profit_prior - kpi.net_profit_current).toLocaleString()})
              </h2>
              <p className="text-xs text-slate-300 mt-1 max-w-3xl leading-relaxed">
                Logistics cost escalation (+13.7%) and AOV shrinkage (-5.1%) account for 83% of total margin degradation. 
                Immediate carrier routing rebalancing and minimum basket size adjustments can recover an estimated $560,000 annually.
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-3 shrink-0">
            <button
              onClick={() => onNavigate('insights')}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold rounded-lg flex items-center space-x-2 transition-all shadow-sm"
            >
              <span>Explore Root Causes</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={() => onNavigate('scenarios')}
              className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold rounded-lg transition-all border border-slate-700"
            >
              Simulate Solutions
            </button>
          </div>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <MetricCard
          label="Net Revenue"
          value={`$${(kpi.revenue_current / 1000000).toFixed(2)}M`}
          priorValue={`$${(kpi.revenue_prior / 1000000).toFixed(2)}M`}
          deltaPct={kpi.revenue_growth_pct}
          isPositiveGood={true}
          subtitle="AOV drop caused $490K top-line drag"
        />
        <MetricCard
          label="Gross Profit"
          value={`$${(kpi.gross_profit_current / 1000000).toFixed(2)}M`}
          priorValue={`$${(kpi.gross_profit_prior / 1000000).toFixed(2)}M`}
          deltaPct={kpi.gross_profit_growth_pct}
          isPositiveGood={true}
          subtitle="Electronics margin eroded 420 bps"
        />
        <MetricCard
          label="Net Operating Profit"
          value={`$${(kpi.net_profit_current / 1000).toFixed(1)}K`}
          priorValue={`$${(kpi.net_profit_prior / 1000).toFixed(1)}K`}
          deltaPct={kpi.net_profit_growth_pct}
          isPositiveGood={true}
          subtitle="Operating margin fell to 11.5%"
          badge="Top Focus"
        />
        <MetricCard
          label="Net Margin"
          value={`${kpi.net_margin_current_pct.toFixed(1)}%`}
          priorValue={`${kpi.net_margin_prior_pct.toFixed(1)}%`}
          deltaPp={kpi.net_margin_delta_pp}
          isPositiveGood={true}
          subtitle="-130 bps overall margin compression"
        />
        <MetricCard
          label="Total Orders"
          value={kpi.orders_current.toLocaleString()}
          priorValue={kpi.orders_prior.toLocaleString()}
          deltaPct={kpi.orders_growth_pct}
          isPositiveGood={true}
          subtitle="Order volume held relatively resilient"
        />
        <MetricCard
          label="Average Order Value"
          value={`$${kpi.aov_current.toFixed(2)}`}
          priorValue={`$${kpi.aov_prior.toFixed(2)}`}
          deltaPct={kpi.aov_growth_pct}
          isPositiveGood={true}
          subtitle="Basket size contracted in discount sales"
          badge="Dilution"
        />
        <MetricCard
          label="Blended CAC"
          value={`$${kpi.cac_current.toFixed(2)}`}
          priorValue={`$${kpi.cac_prior.toFixed(2)}`}
          deltaPct={kpi.cac_growth_pct}
          isPositiveGood={false}
          subtitle="Paid Social CAC surged +38.2%"
        />
        <MetricCard
          label="Customer Churn"
          value={`${kpi.churn_rate_current_pct.toFixed(1)}%`}
          priorValue={`${kpi.churn_rate_prior_pct.toFixed(1)}%`}
          deltaPp={kpi.churn_rate_delta_pp}
          isPositiveGood={false}
          subtitle="Tier-2 defected post delivery fees"
          badge="Retention Alert"
        />
      </div>

      {/* Interactive Sub-Navigation */}
      <div className="flex items-center space-x-2 border-b border-slate-200 pb-2">
        <button
          onClick={() => setActiveSubView('waterfall')}
          className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
            activeSubView === 'waterfall'
              ? 'bg-slate-900 text-white shadow-sm'
              : 'text-slate-600 hover:bg-slate-100'
          }`}
        >
          Executive P&L Waterfall
        </button>
        <button
          onClick={() => setActiveSubView('carriers')}
          className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
            activeSubView === 'carriers'
              ? 'bg-slate-900 text-white shadow-sm'
              : 'text-slate-600 hover:bg-slate-100'
          }`}
        >
          Logistics Carrier Audit
        </button>
        <button
          onClick={() => setActiveSubView('categories')}
          className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
            activeSubView === 'categories'
              ? 'bg-slate-900 text-white shadow-sm'
              : 'text-slate-600 hover:bg-slate-100'
          }`}
        >
          Category Margins & Pareto
        </button>
        <button
          onClick={() => setActiveSubView('trends')}
          className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
            activeSubView === 'trends'
              ? 'bg-slate-900 text-white shadow-sm'
              : 'text-slate-600 hover:bg-slate-100'
          }`}
        >
          Monthly Revenue Trend
        </button>
      </div>

      {/* Dynamic Sub-View Content */}
      {activeSubView === 'waterfall' && (
        <WaterfallChart data={data.p_and_l_waterfall} currency="$" />
      )}

      {activeSubView === 'carriers' && (
        <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-bold text-slate-900 tracking-tight flex items-center space-x-2">
                <Truck className="w-4 h-4 text-blue-600" />
                <span>Shipping Partner Logistics Cost Inflation</span>
              </h3>
              <p className="text-xs text-slate-500">
                Audited fulfillment charges per order. FastLogistics contributed 72% of total logistics variance.
              </p>
            </div>
            <button
              onClick={() => onViewEvidence('ev_shipping_surge')}
              className="text-xs text-blue-600 hover:text-blue-800 font-semibold underline"
            >
              View SQL Audit
            </button>
          </div>

          <div className="border border-slate-200 rounded-lg overflow-hidden">
            <table className="min-w-full divide-y divide-slate-200 text-xs text-left">
              <thead className="bg-slate-50 text-slate-600 font-semibold">
                <tr>
                  <th className="px-4 py-2.5">Carrier Partner</th>
                  <th className="px-4 py-2.5">Q2 Avg Rate</th>
                  <th className="px-4 py-2.5">Q3 Avg Rate</th>
                  <th className="px-4 py-2.5">Rate Delta (%)</th>
                  <th className="px-4 py-2.5">Orders Handled</th>
                  <th className="px-4 py-2.5">Excess Cost Incurred</th>
                  <th className="px-4 py-2.5">Governance Verdict</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200 bg-white">
                {data.shipping_partner_breakdown.map((row) => (
                  <tr key={row.partner} className="hover:bg-slate-50 transition-colors">
                    <td className="px-4 py-2.5 font-bold text-slate-900">{row.partner}</td>
                    <td className="px-4 py-2.5 font-mono text-slate-600">${row.q2_avg_cost.toFixed(2)}</td>
                    <td className="px-4 py-2.5 font-mono font-semibold text-slate-900">${row.q3_avg_cost.toFixed(2)}</td>
                    <td className="px-4 py-2.5">
                      <span className={`px-2 py-0.5 rounded text-[11px] font-semibold ${row.delta_pct > 15 ? 'bg-rose-100 text-rose-800' : 'bg-slate-100 text-slate-700'}`}>
                        +{row.delta_pct.toFixed(1)}%
                      </span>
                    </td>
                    <td className="px-4 py-2.5 font-mono text-slate-600">{row.orders.toLocaleString()}</td>
                    <td className="px-4 py-2.5 font-mono font-bold text-rose-600">+${row.excess_cost.toLocaleString()}</td>
                    <td className="px-4 py-2.5">
                      {row.partner === 'FastLogistics' ? (
                        <span className="text-[11px] text-rose-700 font-bold bg-rose-50 px-2 py-0.5 rounded border border-rose-200">
                          Critical Outlier (Re-route)
                        </span>
                      ) : (
                        <span className="text-[11px] text-emerald-700 font-semibold bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                          Within Target Band
                        </span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {activeSubView === 'categories' && (
        <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-bold text-slate-900 tracking-tight flex items-center space-x-2">
                <Layers className="w-4 h-4 text-blue-600" />
                <span>Product Category Margin & Pareto Contribution</span>
              </h3>
              <p className="text-xs text-slate-500">
                Top 2 categories (Electronics & Fashion) account for 64.3% of cumulative gross margin.
              </p>
            </div>
            <button
              onClick={() => onViewEvidence('ev_category_margin')}
              className="text-xs text-blue-600 hover:text-blue-800 font-semibold underline"
            >
              View SQL Audit
            </button>
          </div>

          <div className="border border-slate-200 rounded-lg overflow-hidden">
            <table className="min-w-full divide-y divide-slate-200 text-xs text-left">
              <thead className="bg-slate-50 text-slate-600 font-semibold">
                <tr>
                  <th className="px-4 py-2.5">Category</th>
                  <th className="px-4 py-2.5">Q3 Net Sales</th>
                  <th className="px-4 py-2.5">Gross Margin ($)</th>
                  <th className="px-4 py-2.5">Gross Margin (%)</th>
                  <th className="px-4 py-2.5">Pareto Contribution</th>
                  <th className="px-4 py-2.5">Margin Trend</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200 bg-white">
                {data.category_performance.map((cat) => (
                  <tr key={cat.category} className="hover:bg-slate-50 transition-colors">
                    <td className="px-4 py-2.5 font-bold text-slate-900">{cat.category}</td>
                    <td className="px-4 py-2.5 font-mono text-slate-600">${cat.revenue.toLocaleString()}</td>
                    <td className="px-4 py-2.5 font-mono font-semibold text-slate-900">${cat.gross_margin.toLocaleString()}</td>
                    <td className="px-4 py-2.5 font-mono font-bold text-blue-600">{cat.margin_pct.toFixed(1)}%</td>
                    <td className="px-4 py-2.5">
                      <div className="flex items-center space-x-2">
                        <div className="w-16 bg-slate-100 h-1.5 rounded-full overflow-hidden">
                          <div className="bg-blue-600 h-full" style={{ width: `${cat.pareto_pct}%` }} />
                        </div>
                        <span className="font-mono text-slate-600 text-[11px]">{cat.pareto_pct.toFixed(1)}%</span>
                      </div>
                    </td>
                    <td className="px-4 py-2.5">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-semibold uppercase ${
                        cat.trend === 'down' ? 'bg-rose-100 text-rose-800' : 'bg-emerald-100 text-emerald-800'
                      }`}>
                        {cat.trend}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {activeSubView === 'trends' && (
        <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm">
          <div className="mb-4">
            <h3 className="text-sm font-bold text-slate-900 tracking-tight flex items-center space-x-2">
              <BarChart3 className="w-4 h-4 text-blue-600" />
              <span>Monthly Revenue & Order Velocity</span>
            </h3>
            <p className="text-xs text-slate-500">Historical performance showing revenue contraction from July through September.</p>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={data.monthly_trend} margin={{ top: 10, right: 20, left: 10, bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="month" tick={{ fontSize: 11, fill: '#64748b' }} />
                <YAxis tick={{ fontSize: 11, fill: '#64748b' }} tickFormatter={(v) => `$${(v/1000000).toFixed(1)}M`} />
                <Tooltip 
                  formatter={(val: any) => [`$${Number(val).toLocaleString()}`, 'Revenue']}
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', color: '#fff', borderRadius: '8px' }}
                />
                <Line type="monotone" dataKey="revenue" stroke="#2563eb" strokeWidth={2.5} dot={{ r: 4 }} activeDot={{ r: 6 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

    </div>
  );
};
