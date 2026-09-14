import React from 'react';
import { BarChart3, Database, FileText, Gauge, Lightbulb, Play, Settings, SlidersHorizontal } from 'lucide-react';

interface NavbarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  onRunDemo: () => void;
  demoLoading: boolean;
  demoProgressStep: string;
}

const navItems = [
  { id: 'dashboard', label: 'Overview', icon: Gauge },
  { id: 'datasets', label: 'Data', icon: Database },
  { id: 'analysis', label: 'Analysis', icon: BarChart3 },
  { id: 'insights', label: 'Insights', icon: Lightbulb },
  { id: 'scenarios', label: 'Scenarios', icon: SlidersHorizontal },
  { id: 'reports', label: 'Reports', icon: FileText },
];

export const Navbar: React.FC<NavbarProps> = ({ activeTab, setActiveTab, onRunDemo, demoLoading, demoProgressStep }) => (
  <header className="sticky top-0 z-40 border-b border-slate-200/90 bg-white/95 backdrop-blur-xl">
    <div className="mx-auto flex h-[72px] max-w-[1440px] items-center gap-6 px-4 sm:px-6 lg:px-8">
      <button onClick={() => setActiveTab('dashboard')} className="group flex shrink-0 items-center gap-3 text-left">
        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-slate-950 text-sm font-black tracking-tight text-white shadow-sm transition group-hover:bg-blue-700">CB</div>
        <div className="hidden sm:block">
          <div className="text-[13px] font-bold tracking-tight text-slate-950">Consulting in a Box</div>
          <div className="text-[10px] font-medium uppercase tracking-[0.18em] text-slate-400">Decision intelligence</div>
        </div>
      </button>

      <div className="h-8 w-px bg-slate-200" />

      <nav className="flex min-w-0 flex-1 items-center gap-1 overflow-x-auto" aria-label="Primary navigation">
        {navItems.map(({ id, label, icon: Icon }) => {
          const active = activeTab === id;
          return (
            <button key={id} onClick={() => setActiveTab(id)} className={`flex shrink-0 items-center gap-2 rounded-lg px-3 py-2 text-xs font-semibold transition ${active ? 'bg-slate-100 text-slate-950' : 'text-slate-500 hover:bg-slate-50 hover:text-slate-900'}`}>
              <Icon className="h-3.5 w-3.5" />
              {label}
            </button>
          );
        })}
      </nav>

      <button onClick={onRunDemo} disabled={demoLoading} className="relative flex shrink-0 items-center gap-2 rounded-lg bg-blue-600 px-3.5 py-2.5 text-xs font-bold text-white shadow-sm transition hover:bg-blue-700 disabled:cursor-wait disabled:opacity-70">
        <Play className="h-3.5 w-3.5 fill-current" />
        <span className="hidden md:inline">Run demo</span>
        {demoLoading && <span className="hidden xl:inline font-medium text-blue-100">· {demoProgressStep}</span>}
      </button>

      <button onClick={() => setActiveTab('settings')} className={`hidden rounded-lg p-2.5 transition lg:block ${activeTab === 'settings' ? 'bg-slate-100 text-slate-900' : 'text-slate-400 hover:bg-slate-50 hover:text-slate-700'}`} aria-label="Settings">
        <Settings className="h-4 w-4" />
      </button>
    </div>
  </header>
);
