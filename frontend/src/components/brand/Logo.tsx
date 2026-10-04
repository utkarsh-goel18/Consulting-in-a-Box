import React from 'react';

interface LogoProps {
  size?: number;
  showWordmark?: boolean;
  compact?: boolean;
}

/**
 * Consulting in a Box brand mark.
 * Four rising bars represent DATA → INSIGHT → DECISION,
 * with a sweeping arc and endpoint forming the analytical growth motif.
 */
export const Logo: React.FC<LogoProps> = ({ size = 42, showWordmark = false, compact = false }) => (
  <div className="flex items-center gap-3">
    <svg
      width={size}
      height={size}
      viewBox="0 0 48 48"
      role="img"
      aria-label="Consulting in a Box logo"
      className="shrink-0"
    >
      <defs>
        <linearGradient id="cibLogoBars" x1="10" y1="36" x2="36" y2="10" gradientUnits="userSpaceOnUse">
          <stop offset="0" stopColor="#1677e8" />
          <stop offset="1" stopColor="#1186dc" />
        </linearGradient>
        <linearGradient id="cibLogoDot" x1="33" y1="24" x2="38" y2="18" gradientUnits="userSpaceOnUse">
          <stop offset="0" stopColor="#0ea5c9" />
          <stop offset="1" stopColor="#06b6d4" />
        </linearGradient>
      </defs>

      {/* Light rounded-square brand tile */}
      <rect x="1" y="1" width="46" height="46" rx="14" fill="#ffffff" />

      {/* Rising analytical bars */}
      <path
        d="M12 34V25.5M20 34V19M28 34V13M36 34V9"
        stroke="url(#cibLogoBars)"
        strokeWidth="5"
        strokeLinecap="round"
      />

      {/* Sweeping growth arc */}
      <path
        d="M10.5 18.5C15.4 12.6 21.7 9.9 27.4 11.2C31.9 12.2 34.2 15.3 36.3 18.7"
        fill="none"
        stroke="#0ea5c9"
        strokeWidth="2.2"
        strokeLinecap="round"
        opacity=".95"
      />

      {/* Decision endpoint */}
      <circle cx="36.5" cy="18.8" r="3" fill="url(#cibLogoDot)" />
    </svg>

    {showWordmark && !compact && (
      <div className="leading-none">
        <div className="text-[13px] font-bold tracking-tight text-slate-950 dark-brand-text">Consulting in a Box</div>
        <div className="mt-1 text-[9px] font-semibold uppercase tracking-[0.18em] text-slate-400">Decision intelligence</div>
      </div>
    )}
  </div>
);
