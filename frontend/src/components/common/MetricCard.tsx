import React from 'react';
import { ArrowUpRight, ArrowDownRight, Minus } from 'lucide-react';

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
  const isDelta = deltaPct !== undefined || deltaPp !== undefined;
  const rawDelta = deltaPct !== undefined ? deltaPct : (deltaPp || 0);
  const isNeutral = rawDelta === 0;
  const isPositive = rawDelta > 0;
  
  // Decide favorable vs unfavorable
  const isFavorable = isPositiveGood ? isPositive : !isPositive;

  return (
    <div
      onClick={onClick}
      className={`bg-white border border-slate-200 rounded-lg p-4 shadow-sm hover:border-slate-300 transition-all ${
        onClick ? 'cursor-pointer hover:shadow-md' : ''
      }`}
    >
      <div className="flex items-center justify-between mb-1.5">
        <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">{label}</span>
        {badge && (
          <span className="text-[10px] font-medium px-2 py-0.5 rounded bg-slate-100 text-slate-600 border border-slate-200">
            {badge}
          </span>
        )}
      </div>

      <div className="flex items-baseline space-x-2">
        <span className="text-2xl font-bold tracking-tight text-slate-900">{value}</span>
      </div>

      {isDelta && (
        <div className="flex items-center space-x-1.5 mt-2">
          <div
            className={`inline-flex items-center px-1.5 py-0.5 rounded text-xs font-semibold ${
              isNeutral
                ? 'bg-slate-100 text-slate-600'
                : isFavorable
                ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                : 'bg-rose-50 text-rose-700 border border-rose-200'
            }`}
          >
            {isNeutral ? (
              <Minus className="w-3 h-3 mr-0.5" />
            ) : isPositive ? (
              <ArrowUpRight className="w-3 h-3 mr-0.5" />
            ) : (
              <ArrowDownRight className="w-3 h-3 mr-0.5" />
            )}
            <span>
              {deltaPct !== undefined ? `${isPositive ? '+' : ''}${deltaPct.toFixed(1)}%` : `${isPositive ? '+' : ''}${deltaPp?.toFixed(1)} pp`}
            </span>
          </div>
          {priorValue && <span className="text-[11px] text-slate-400">vs {priorValue} prior</span>}
        </div>
      )}

      {subtitle && <p className="text-[11px] text-slate-500 mt-2 line-clamp-1">{subtitle}</p>}
    </div>
  );
};
