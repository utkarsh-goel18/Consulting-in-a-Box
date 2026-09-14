import React from 'react';
import { ArrowDownRight, ArrowUpRight, Minus } from 'lucide-react';

interface MetricCardProps {
  label: string;
  value: string;
  priorValue?: string;
  deltaPct?: number;
  deltaPp?: number;
  isPositiveGood?: boolean;
  subtitle?: string;
  badge?: string;
  onClick?: () => void;
}

export const MetricCard: React.FC<MetricCardProps> = ({
  label,
  value,
  priorValue,
  deltaPct,
  deltaPp,
  isPositiveGood = true,
  subtitle,
  badge,
  onClick,
}) => {
  const rawDelta = deltaPct ?? deltaPp ?? 0;
  const neutral = rawDelta === 0;
  const positive = rawDelta > 0;
  const favorable = isPositiveGood ? positive : !positive;

  return (
    <div
      onClick={onClick}
      className={`group rounded-2xl border border-slate-200 bg-white p-5 shadow-[0_1px_2px_rgba(15,23,42,0.03)] transition duration-200 hover:-translate-y-0.5 hover:border-slate-300 hover:shadow-[0_10px_30px_rgba(15,23,42,0.06)] ${onClick ? 'cursor-pointer' : ''}`}
    >
      <div className="flex items-start justify-between gap-3">
        <span className="text-[11px] font-bold uppercase tracking-[0.14em] text-slate-400">{label}</span>
        {badge && (
          <span className="rounded-full border border-slate-200 bg-slate-50 px-2 py-1 text-[9px] font-bold uppercase tracking-wider text-slate-500">
            {badge}
          </span>
        )}
      </div>

      <div className="mt-3 flex items-end gap-2">
        <span className="text-[27px] font-bold leading-none tracking-[-0.04em] text-slate-950">{value}</span>
      </div>

      {rawDelta !== undefined && (
        <div className="mt-3 flex items-center gap-2">
          <span className={`inline-flex items-center gap-0.5 rounded-md px-1.5 py-1 text-[10px] font-bold ${
            neutral ? 'bg-slate-100 text-slate-500' : favorable ? 'bg-emerald-50 text-emerald-700' : 'bg-rose-50 text-rose-700'
          }`}>
            {neutral ? <Minus className="h-3 w-3" /> : positive ? <ArrowUpRight className="h-3 w-3" /> : <ArrowDownRight className="h-3 w-3" />}
            {deltaPct !== undefined ? `${positive ? '+' : ''}${deltaPct.toFixed(1)}%` : `${positive ? '+' : ''}${(deltaPp ?? 0).toFixed(1)} pp`}
          </span>
          {priorValue && <span className="text-[10px] text-slate-400">vs {priorValue}</span>}
        </div>
      )}

      {subtitle && <p className="mt-3 truncate border-t border-slate-100 pt-3 text-[10px] leading-4 text-slate-500">{subtitle}</p>}
    </div>
  );
};
