import React, { useState } from 'react';

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
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);

  const width = 1100;
  const height = 360;
  const margin = { top: 28, right: 24, bottom: 82, left: 82 };
  const plotWidth = width - margin.left - margin.right;
  const plotHeight = height - margin.top - margin.bottom;

  const safeData = data.map((item) => ({
    ...item,
    amount: Number.isFinite(Number(item.amount)) ? Number(item.amount) : 0,
    running_total: item.running_total == null ? undefined : Number(item.running_total),
  }));

  // Totals are absolute profit benchmarks. Drivers are signed impacts from zero.
  const values = safeData.flatMap((item) => {
    if (item.type === 'total') return [0, Math.abs(item.amount)];
    return [0, item.amount];
  });
  const maxAbs = Math.max(...values.map(Math.abs), 1);
  const range = maxAbs * 1.12;
  const y = (value: number) => margin.top + ((range - value) / (2 * range)) * plotHeight;
  const zeroY = y(0);
  const barWidth = Math.min(110, Math.max(52, plotWidth / Math.max(safeData.length * 1.65, 1)));
  const stepGap = plotWidth / Math.max(safeData.length, 1);

  const formatAxis = (value: number) => {
    const abs = Math.abs(value);
    const sign = value < 0 ? '-' : '';
    if (abs >= 10_000_000) return `${sign}${currency}${(abs / 10_000_000).toFixed(1)}Cr`;
    if (abs >= 100_000) return `${sign}${currency}${(abs / 100_000).toFixed(1)}L`;
    if (abs >= 1_000) return `${sign}${currency}${(abs / 1_000).toFixed(0)}K`;
    return `${sign}${currency}${abs.toLocaleString('en-IN')}`;
  };

  const formatAmount = (value: number) => `${value < 0 ? '-' : '+'}${currency}${Math.abs(value).toLocaleString('en-IN')}`;

  const ticks = [-range, -range / 2, 0, range / 2, range];
  const hoveredItem = hoveredIndex == null ? null : safeData[hoveredIndex];

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
      <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h3 className="text-sm font-bold tracking-tight text-slate-900 dark:text-white">Executive P&amp;L Waterfall Bridge</h3>
          <p className="mt-1 text-xs text-slate-500">Prior-period profit → profit-impact drivers → current-period profit.</p>
        </div>
        <div className="flex items-center gap-4 text-[11px] text-slate-500">
          <span className="flex items-center gap-1.5"><span className="h-2.5 w-2.5 rounded-sm bg-slate-700" />Benchmark</span>
          <span className="flex items-center gap-1.5"><span className="h-2.5 w-2.5 rounded-sm bg-rose-600" />Unfavorable</span>
          <span className="flex items-center gap-1.5"><span className="h-2.5 w-2.5 rounded-sm bg-emerald-600" />Favorable</span>
        </div>
      </div>

      <div className="h-80 w-full overflow-x-auto">
        <svg viewBox={`0 0 ${width} ${height}`} width="100%" height="100%" role="img" aria-label="P and L impact bar chart">
          <defs>
            <style>{`.wf-label{font-family:Inter,ui-sans-serif,system-ui,sans-serif}`}</style>
          </defs>

          {ticks.map((tick) => (
            <g key={`tick-${tick}`}>
              <line x1={margin.left} x2={width - margin.right} y1={y(tick)} y2={y(tick)} stroke="currentColor" opacity={tick === 0 ? 0.35 : 0.12} strokeDasharray={tick === 0 ? undefined : '3 3'} />
              <text className="wf-label" x={margin.left - 10} y={y(tick) + 4} textAnchor="end" fontSize="10" fill="currentColor" opacity="0.65">{formatAxis(tick)}</text>
            </g>
          ))}

          <line x1={margin.left} x2={width - margin.right} y1={zeroY} y2={zeroY} stroke="currentColor" opacity="0.5" strokeWidth="1.5" />

          {safeData.map((item, index) => {
            const x = margin.left + stepGap * index + (stepGap - barWidth) / 2;
            const isTotal = item.type === 'total';
            const value = isTotal ? Math.abs(item.amount) : item.amount;
            const topValue = Math.max(value, 0);
            const bottomValue = Math.min(value, 0);
            const top = y(topValue);
            const bottom = y(bottomValue);
            const rectY = isTotal ? y(value) : top;
            const rectHeight = Math.max(2, Math.abs(bottom - top));
            const fill = isTotal ? '#334155' : value < 0 ? '#e11d48' : '#059669';
            const labelY = margin.top + plotHeight + 20;
            const isHovered = hoveredIndex === index;

            return (
              <g
                key={`${item.step}-${index}`}
                onMouseEnter={() => setHoveredIndex(index)}
                onMouseLeave={() => setHoveredIndex(null)}
                className="cursor-pointer"
              >
                <rect x={x} y={rectY} width={barWidth} height={rectHeight} rx="5" fill={fill} opacity={isHovered ? '1' : '0.96'} stroke={isHovered ? 'currentColor' : 'none'} strokeWidth="1.5" />
                <text className="wf-label" x={x + barWidth / 2} y={labelY} textAnchor="middle" fontSize="10" fill="currentColor" opacity="0.7" transform={`rotate(-18 ${x + barWidth / 2} ${labelY})`}>{item.step}</text>
              </g>
            );
          })}

          {hoveredItem && hoveredIndex != null && (() => {
            const item = hoveredItem;
            const x = margin.left + stepGap * hoveredIndex + (stepGap - barWidth) / 2;
            const isTotal = item.type === 'total';
            const value = isTotal ? Math.abs(item.amount) : item.amount;
            const barTop = y(Math.max(value, 0));
            const barBottom = y(Math.min(value, 0));
            const tooltipText = isTotal
              ? `${item.step}: ${currency}${Math.abs(item.amount).toLocaleString('en-IN')}`
              : `${item.step}: ${formatAmount(item.amount)}`;
            const tooltipWidth = Math.min(250, Math.max(130, tooltipText.length * 6.4 + 20));
            const tooltipX = Math.min(width - margin.right - tooltipWidth, Math.max(margin.left, x + barWidth / 2 - tooltipWidth / 2));
            const rawTooltipY = isTotal || value >= 0 ? barTop - 42 : barBottom + 12;
            const tooltipY = Math.max(4, Math.min(height - 30, rawTooltipY));

            return (
              <g pointerEvents="none">
                <rect x={tooltipX} y={tooltipY} width={tooltipWidth} height="28" rx="6" fill="#0f172a" opacity="0.96" />
                <text className="wf-label" x={tooltipX + tooltipWidth / 2} y={tooltipY + 18} textAnchor="middle" fontSize="11" fontWeight="600" fill="white">{tooltipText}</text>
              </g>
            );
          })()}
        </svg>
      </div>
    </div>
  );
};