import React, { useMemo, useState } from 'react';

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

const formatCompact = (value: number, currency: string) => {
  const abs = Math.abs(value);
  const sign = value < 0 ? '-' : '';
  if (abs >= 10_000_000) return `${sign}${currency}${(abs / 10_000_000).toFixed(1)}Cr`;
  if (abs >= 100_000) return `${sign}${currency}${(abs / 100_000).toFixed(1)}L`;
  if (abs >= 1_000) return `${sign}${currency}${(abs / 1_000).toFixed(0)}K`;
  return `${sign}${currency}${Math.round(abs).toLocaleString('en-IN')}`;
};

const formatAmount = (value: number, currency: string) =>
  `${value < 0 ? '-' : '+'}${currency}${Math.abs(value).toLocaleString('en-IN', { maximumFractionDigits: 0 })}`;

/**
 * Executive P&L waterfall.
 *
 * This is intentionally rendered with SVG rather than a stacked Recharts bar.
 * A conventional stacked bar chart cannot reliably represent a floating
 * negative segment: Recharts maintains separate positive/negative stacks,
 * which can make a negative impact appear anchored at zero. Here every bar is
 * explicitly positioned between its two actual P&L totals, so the zero line
 * is always the true zero line and positive/negative impacts are unambiguous.
 */
export const WaterfallChart: React.FC<WaterfallChartProps> = ({ data, currency = '₹' }) => {
  const [hovered, setHovered] = useState<number | null>(null);

  const prepared = useMemo(() => data.map((item) => {
    if (item.type === 'total') {
      return {
        ...item,
        from: 0,
        to: item.amount,
        isTotal: true,
      };
    }

    const to = item.running_total ?? item.amount;
    const from = to - item.amount;

    return {
      ...item,
      from,
      to,
      isTotal: false,
    };
  }), [data]);

  const bounds = useMemo(() => {
    const values = prepared.flatMap((item) => [item.from, item.to]);
    const rawMin = Math.min(0, ...values);
    const rawMax = Math.max(0, ...values);
    const range = Math.max(rawMax - rawMin, 1);
    const padding = range * 0.08;
    return {
      min: rawMin - padding,
      max: rawMax + padding,
    };
  }, [prepared]);

  const viewWidth = 1200;
  const viewHeight = 420;
  const plot = { left: 78, right: 24, top: 22, bottom: 92 };
  const plotWidth = viewWidth - plot.left - plot.right;
  const plotHeight = viewHeight - plot.top - plot.bottom;
  const yScale = (value: number) =>
    plot.top + ((bounds.max - value) / (bounds.max - bounds.min)) * plotHeight;

  const zeroY = yScale(0);
  const slotWidth = plotWidth / Math.max(prepared.length, 1);
  const barWidth = Math.min(108, slotWidth * 0.62);

  const gridValues = Array.from({ length: 5 }, (_, index) =>
    bounds.max - ((bounds.max - bounds.min) * index) / 4,
  );

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
      <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h3 className="text-sm font-bold tracking-tight text-slate-900 dark:text-white">
            Executive P&amp;L Waterfall Bridge
          </h3>
          <p className="mt-1 text-xs text-slate-500">
            Prior-period profit → profit-impact drivers → current-period profit.
          </p>
        </div>
        <div className="flex items-center gap-4 text-[11px] text-slate-500">
          <span className="flex items-center gap-1.5">
            <span className="h-2.5 w-2.5 rounded-sm bg-slate-700" />Benchmark
          </span>
          <span className="flex items-center gap-1.5">
            <span className="h-2.5 w-2.5 rounded-sm bg-rose-600" />Unfavorable
          </span>
          <span className="flex items-center gap-1.5">
            <span className="h-2.5 w-2.5 rounded-sm bg-emerald-600" />Favorable
          </span>
        </div>
      </div>

      <div className="h-80 w-full overflow-hidden">
        <svg
          viewBox={`0 0 ${viewWidth} ${viewHeight}`}
          className="h-full w-full"
          role="img"
          aria-label="Executive P&L waterfall bridge"
        >
          {/* Grid and correctly positioned zero reference line */}
          {gridValues.map((value, index) => {
            const y = yScale(value);
            return (
              <g key={`grid-${index}`}>
                <line
                  x1={plot.left}
                  x2={viewWidth - plot.right}
                  y1={y}
                  y2={y}
                  stroke="#64748b"
                  strokeDasharray="3 3"
                  opacity={0.18}
                />
                <text
                  x={plot.left - 10}
                  y={y + 4}
                  textAnchor="end"
                  fontSize="10"
                  fill="#64748b"
                >
                  {formatCompact(value, currency)}
                </text>
              </g>
            );
          })}

          <line
            x1={plot.left}
            x2={viewWidth - plot.right}
            y1={zeroY}
            y2={zeroY}
            stroke="#94a3b8"
            strokeWidth="1.4"
          />

          {prepared.map((item, index) => {
            const centerX = plot.left + slotWidth * (index + 0.5);
            const top = yScale(Math.max(item.from, item.to));
            const bottom = yScale(Math.min(item.from, item.to));
            const height = Math.max(bottom - top, item.amount === 0 ? 2 : 3);
            const x = centerX - barWidth / 2;
            const fill = item.isTotal
              ? '#334155'
              : item.amount < 0 || item.type === 'negative'
                ? '#e11d48'
                : '#059669';
            const labelY = plot.top + plotHeight + 26;
            const isHovered = hovered === index;

            return (
              <g
                key={`${item.step}-${index}`}
                onMouseEnter={() => setHovered(index)}
                onMouseLeave={() => setHovered(null)}
                className="cursor-pointer"
              >
                <rect
                  x={x}
                  y={top}
                  width={barWidth}
                  height={height}
                  rx="5"
                  fill={fill}
                  opacity={isHovered ? 0.82 : 1}
                />

                {!item.isTotal && (
                  <line
                    x1={centerX}
                    x2={centerX}
                    y1={top}
                    y2={bottom}
                    stroke={fill}
                    strokeWidth="1"
                    opacity={0.35}
                  />
                )}

                <text
                  x={centerX}
                  y={labelY}
                  textAnchor="end"
                  transform={`rotate(-18 ${centerX} ${labelY})`}
                  fontSize="10"
                  fill="#64748b"
                >
                  {item.step}
                </text>

                {isHovered && (
                  <g>
                    <rect
                      x={Math.max(6, Math.min(viewWidth - 230, centerX - 110))}
                      y={Math.max(8, top - 58)}
                      width="220"
                      height="48"
                      rx="7"
                      fill="#020617"
                      stroke="#334155"
                    />
                    <text
                      x={Math.max(16, Math.min(viewWidth - 220, centerX - 100))}
                      y={Math.max(27, top - 39)}
                      fontSize="11"
                      fontWeight="700"
                      fill="#e2e8f0"
                    >
                      {item.step}
                    </text>
                    <text
                      x={Math.max(16, Math.min(viewWidth - 220, centerX - 100))}
                      y={Math.max(45, top - 21)}
                      fontSize="11"
                      fill={item.isTotal ? '#e2e8f0' : fill}
                    >
                      {item.isTotal
                        ? `${currency}${Math.abs(item.amount).toLocaleString('en-IN', { maximumFractionDigits: 0 })}`
                        : `${formatAmount(item.amount, currency)}  |  ${formatCompact(item.from, currency)} → ${formatCompact(item.to, currency)}`}
                    </text>
                  </g>
                )}
              </g>
            );
          })}
        </svg>
      </div>
    </div>
  );
};
