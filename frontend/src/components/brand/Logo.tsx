import React from 'react';

interface LogoProps {
  size?: number;
  showWordmark?: boolean;
  compact?: boolean;
}

/**
 * Consulting in a Box brand mark.
 * The three rising bars represent DATA → INSIGHT → DECISION,
 * while the connected line forms a subtle C/B monogram.
 */
export const Logo: React.FC<LogoProps> = ({ size = 42, showWordmark = false, compact = false }) => (
  <div className="flex items-center gap-3">
    <svg width={size} height={size} viewBox="0 0 48 48" role="img" aria-label="Consulting in a Box logo" className="shrink-0">
      <defs>
        <linearGradient id="cibLogoGradient" x1="7" y1="42" x2="41" y2="6" gradientUnits="userSpaceOnUse">
          <stop offset="0" stopColor="#2563eb" />
          <stop offset="1" stopColor="#06b6d4" />
        </linearGradient>
      </defs>
      <rect x="1" y="1" width="46" height="46" rx="13" fill="currentColor" className="text-slate-950 dark-logo-surface" />
      <path d="M13 34V25M20 34V19M27 34V14M34 34V9" stroke="url(#cibLogoGradient)" strokeWidth="4" strokeLinecap="round" />
      <path d="M10 36.5H37" stroke="white" strokeOpacity=".18" strokeWidth="1.5" strokeLinecap="round" />
      <path d="M12 16.5C16.2 11.9 21.3 10.1 26.3 11.3C30.7 12.4 33.5 15.5 36 18.8" fill="none" stroke="white" strokeWidth="1.7" strokeLinecap="round" strokeOpacity=".9" />
      <circle cx="36" cy="18.8" r="2.1" fill="#06b6d4" />
    </svg>
    {showWordmark && !compact && (
      <div className="leading-none">
        <div className="text-[13px] font-bold tracking-tight text-slate-950 dark-brand-text">Consulting in a Box</div>
        <div className="mt-1 text-[9px] font-semibold uppercase tracking-[0.18em] text-slate-400">Decision intelligence</div>
      </div>
    )}
  </div>
);
