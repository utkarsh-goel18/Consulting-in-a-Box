import React from 'react';
import { 
  ResponsiveContainer, 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  Tooltip, 
  Cell, 
  CartesianGrid, 
  ReferenceLine 
} from 'recharts';

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

export const WaterfallChart: React.FC<WaterfallChartProps> = ({ data, currency = '$' }) => {
  // Format data for Recharts stacked waterfall representation
  // For total bars: base = 0, value = amount
  // For negative delta: base = running_total, value = abs(amount)
  // For positive delta: base = running_total - amount, value = amount
  let running = 0;
  const chartData = data.map((item, index) => {
    if (item.type === 'total') {
      running = item.amount;
      return {
        step: item.step,
        base: 0,
        value: item.amount,
        type: item.type,
        displayAmount: item.amount
      };
    } else {
      const prior = running;
      running = prior + item.amount;
      const base = item.amount < 0 ? running : prior;
      return {
        step: item.step,
        base: Math.max(0, base),
        value: Math.abs(item.amount),
        type: item.type,
        displayAmount: item.amount
      };
    }
  });

  const getBarColor = (type: string, amount: number) => {
    if (type === 'total') return '#1e293b'; // Slate 800
    if (amount < 0 || type === 'negative') return '#e11d48'; // Rose 600
    return '#059669'; // Emerald 600
  };

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const item = payload[0].payload;
      return (
        <div className="bg-slate-900 text-white p-3 rounded-lg shadow-lg border border-slate-800 text-xs font-mono">
          <p className="font-bold text-slate-200 mb-1">{item.step}</p>
          <p className="flex justify-between space-x-4">
            <span className="text-slate-400">Variance:</span>
            <span className={item.displayAmount < 0 ? 'text-rose-400' : (item.type === 'total' ? 'text-blue-400' : 'text-emerald-400')}>
              {item.displayAmount < 0 ? '-' : (item.type === 'total' ? '' : '+')}
              {currency}{Math.abs(item.displayAmount).toLocaleString()}
            </span>
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-sm font-bold text-slate-900 tracking-tight">Executive P&L Waterfall Bridge</h3>
          <p className="text-xs text-slate-500">Decomposition from Prior Net Profit to Current Net Profit across major cost centers.</p>
        </div>
        <div className="flex items-center space-x-3 text-xs font-mono">
          <span className="flex items-center space-x-1">
            <span className="w-2.5 h-2.5 rounded-sm bg-slate-800" />
            <span className="text-slate-600">Net Profit Benchmark</span>
          </span>
          <span className="flex items-center space-x-1">
            <span className="w-2.5 h-2.5 rounded-sm bg-rose-600" />
            <span className="text-slate-600">Unfavorable Drift</span>
          </span>
        </div>
      </div>

      <div className="h-72 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData} margin={{ top: 20, right: 20, left: 20, bottom: 40 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
            <XAxis 
              dataKey="step" 
              tick={{ fontSize: 11, fill: '#64748b' }} 
              interval={0}
              angle={-20}
              textAnchor="end"
              height={50}
            />
            <YAxis 
              tick={{ fontSize: 11, fill: '#64748b' }} 
              tickFormatter={(v) => `${currency}${(v / 1000).toFixed(0)}k`}
            />
            <Tooltip content={<CustomTooltip />} />
            <ReferenceLine y={0} stroke="#94a3b8" />
            
            {/* Transparent base for floating waterfall steps */}
            <Bar dataKey="base" stackId="waterfall" fill="transparent" />
            
            {/* The colored floating delta */}
            <Bar dataKey="value" stackId="waterfall" radius={[4, 4, 4, 4]}>
              {chartData.map((entry, idx) => (
                <Cell key={`cell-${idx}`} fill={getBarColor(entry.type, entry.displayAmount)} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
