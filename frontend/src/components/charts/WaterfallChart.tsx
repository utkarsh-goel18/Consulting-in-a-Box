import React from 'react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Cell, CartesianGrid, ReferenceLine } from 'recharts';

interface WaterfallStep {
  step: string;
  amount: number;
  type: string;
  running_total?: number;
}

interface WaterfallChartProps {
  data: WaterfallStep[];
  currency?: string;
}

export const WaterfallChart: React.FC<WaterfallChartProps> = ({ data, currency = '₹' }) => {
  let running = 0;
  const chartData = data.map((item) => {
    if (item.type === 'total') {
      running = item.amount;
      return { step: item.step, base: 0, value: Math.abs(item.amount), type: item.type, displayAmount: item.amount };
    }

    const prior = running;
    running = prior + item.amount;
    // Keep negative running totals negative. Clamping the base to zero was
    // hiding every unfavorable bridge step when profit was below zero.
    const base = item.amount < 0 ? running : prior;
    return { step: item.step, base, value: Math.abs(item.amount), type: item.type, displayAmount: item.amount };
  });

  const getBarColor = (type: string, amount: number) => {
    if (type === 'total') return '#334155';
    if (amount < 0 || type === 'negative') return '#e11d48';
    return '#059669';
  };

  const formatAxis = (value: number) => {
    const abs = Math.abs(value);
    const sign = value < 0 ? '-' : '';
    if (abs >= 10_000_000) return `${sign}${currency}${(abs / 10_000_000).toFixed(1)}Cr`;
    if (abs >= 100_000) return `${sign}${currency}${(abs / 100_000).toFixed(1)}L`;
    if (abs >= 1_000) return `${sign}${currency}${(abs / 1_000).toFixed(0)}K`;
    return `${sign}${currency}${abs.toLocaleString('en-IN')}`;
  };

  const CustomTooltip = ({ active, payload }: any) => {
    if (!active || !payload?.length) return null;
    const item = payload[0].payload;
    return (
      <div className="rounded-lg border border-slate-700 bg-slate-950 p-3 text-xs text-white shadow-xl">
        <p className="mb-1 font-bold text-slate-200">{item.step}</p>
        <p className={item.displayAmount < 0 ? 'text-rose-400' : 'text-emerald-400'}>
          {item.displayAmount < 0 ? '-' : item.type === 'total' ? '' : '+'}
          {currency}{Math.abs(item.displayAmount).toLocaleString('en-IN')}
        </p>
      </div>
    );
  };

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
      <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h3 className="text-sm font-bold tracking-tight text-slate-900 dark:text-white">Executive P&L Waterfall Bridge</h3>
          <p className="mt-1 text-xs text-slate-500">Prior-period profit → modeled drivers → current-period profit.</p>
        </div>
        <div className="flex items-center gap-4 text-[11px] text-slate-500">
          <span className="flex items-center gap-1.5"><span className="h-2.5 w-2.5 rounded-sm bg-slate-700" />Benchmark</span>
          <span className="flex items-center gap-1.5"><span className="h-2.5 w-2.5 rounded-sm bg-rose-600" />Unfavorable</span>
          <span className="flex items-center gap-1.5"><span className="h-2.5 w-2.5 rounded-sm bg-emerald-600" />Favorable</span>
        </div>
      </div>
      <div className="h-80 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData} margin={{ top: 20, right: 20, left: 20, bottom: 55 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#64748b" opacity={0.18} vertical={false} />
            <XAxis dataKey="step" tick={{ fontSize: 10, fill: '#64748b' }} interval={0} angle={-18} textAnchor="end" height={65} />
            <YAxis tick={{ fontSize: 10, fill: '#64748b' }} tickFormatter={formatAxis} />
            <Tooltip cursor={{ fill: 'rgba(148,163,184,0.08)' }} content={<CustomTooltip />} />
            <ReferenceLine y={0} stroke="#94a3b8" />
            <Bar dataKey="base" stackId="waterfall" fill="transparent" />
            <Bar dataKey="value" stackId="waterfall" radius={[4, 4, 4, 4]}>
              {chartData.map((entry, idx) => <Cell key={`cell-${idx}`} fill={getBarColor(entry.type, entry.displayAmount)} />)}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
