import React from 'react';
import { BarChart3, Database, FileText, Gauge, Lightbulb, Moon, Play, Settings, SlidersHorizontal, Sun } from 'lucide-react';
import { Logo } from '../brand/Logo';

interface NavbarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  onRunDemo: () => void;
  demoLoading: boolean;
  demoProgressStep: string;
  darkMode: boolean;
  onToggleTheme: () => void;
}

const navItems = [
  { id: 'dashboard', label: 'Overview', icon: Gauge },
  { id: 'datasets', label: 'Data', icon: Database },
  { id: 'analysis', label: 'Analysis', icon: BarChart3 },
  { id: 'insights', label: 'Insights', icon: Lightbulb },
  { id: 'scenarios', label: 'Scenarios', icon: SlidersHorizontal },
  { id: 'reports', label: 'Reports', icon: FileText },
];

export const Navbar: React.FC<NavbarProps> = ({
  activeTab,
  setActiveTab,
  onRunDemo,
  demoLoading,
  demoProgressStep,
  darkMode,
  onToggleTheme,
}) => (
  <header className="sticky top-0 z-40 border-b border-slate-200/90 bg-white/95 backdrop-blur-xl dark:border-slate-800 dark:bg-[#0f172a]/95">
    <div className="mx-auto flex h-[72px] max-w-[1440px] items-center gap-4 px-4 sm:px-6 lg:px-8">
      <button onClick={() => setActiveTab('dashboard')} className="group flex shrink-0 items-center text-left" aria-label="Go to overview">
        <Logo size={40} showWordmark />
      </button>

      <div className="hidden h-8 w-px bg-slate-200 dark:bg-slate-700 md:block" />

      <nav className="flex min-w-0 flex-1 items-center gap-1 overflow-x-auto" aria-label="Primary navigation">
        {navItems.map(({ id, label, icon: Icon }) => {
          const active = activeTab === id;
          return (
            <button key={id} onClick={() => setActiveTab(id)} className={`flex shrink-0 items-center gap-2 rounded-lg px-3 py-2 text-xs font-semibold transition ${active ? 'bg-slate-100 text-slate-950 dark:bg-slate-800 dark:text-white' : 'text-slate-500 hover:bg-slate-50 hover:text-slate-900 dark:text-slate-400 dark:hover:bg-slate-800/70 dark:hover:text-slate-100'}`}>
              <Icon className="h-3.5 w-3.5" />
              {label}
            </button>
          );
        })}
      </nav>

      <button onClick={onRunDemo} disabled={demoLoading} className="relative flex shrink-0 items-center gap-2 rounded-lg bg-blue-600 px-3.5 py-2.5 text-xs font-bold text-white shadow-sm transition hover:bg-blue-700 disabled:cursor-wait disabled:opacity-70">
        <Play className="h-3.5 w-3.5 fill-current" />
        <span className="hidden md:inline">Run Demo Engagement</span>
        {demoLoading && <span className="hidden xl:inline font-medium text-blue-100">· {demoProgressStep}</span>}
      </button>

      <button
        onClick={onToggleTheme}
        className="rounded-lg border border-slate-200 p-2.5 text-slate-500 transition hover:bg-slate-50 hover:text-slate-900 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800 dark:hover:text-white"
        aria-label={darkMode ? 'Switch to light mode' : 'Switch to dark mode'}
        title={darkMode ? 'Light mode' : 'Dark mode'}
      >
        {darkMode ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
      </button>

      <button onClick={() => setActiveTab('settings')} className={`rounded-lg p-2.5 transition ${activeTab === 'settings' ? 'bg-slate-100 text-slate-900 dark:bg-slate-800 dark:text-white' : 'text-slate-400 hover:bg-slate-50 hover:text-slate-700 dark:hover:bg-slate-800 dark:hover:text-slate-200'}`} aria-label="Settings">
        <Settings className="h-4 w-4" />
      </button>
    </div>
  </header>
);
