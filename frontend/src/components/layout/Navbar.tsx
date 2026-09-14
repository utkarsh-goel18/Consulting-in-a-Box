import React from 'react';
import { 
  BarChart3, 
  Database, 
  FileText, 
  Sliders, 
  GitFork, 
  Compass, 
  Settings as SettingsIcon, 
  Play, 
  CheckCircle2, 
  Loader2, 
  Sparkles
} from 'lucide-react';

interface NavbarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  onRunDemo: () => void;
  demoLoading: boolean;
  demoProgressStep: string;
}

export const Navbar: React.FC<NavbarProps> = ({
  activeTab,
  setActiveTab,
  onRunDemo,
  demoLoading,
  demoProgressStep,
}) => {
  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: BarChart3 },
    { id: 'datasets', label: 'Datasets', icon: Database },
    { id: 'analysis', label: 'Analysis', icon: Compass },
    { id: 'insights', label: 'Insights', icon: GitFork },
    { id: 'scenarios', label: 'Scenarios', icon: Sliders },
    { id: 'reports', label: 'Reports', icon: FileText },
    { id: 'settings', label: 'Settings', icon: SettingsIcon },
  ];

  const workflowSteps = [
    'UPLOAD DATA',
    'DEFINE PROBLEM',
    'ANALYZE',
    'IDENTIFY DRIVERS',
    'RECOMMEND',
    'SIMULATE'
  ];

  return (
    <header className="bg-corporate-900 border-b border-corporate-800 text-white sticky top-0 z-50">
      {/* Top Brand Bar */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo & Subtitle */}
          <div className="flex items-center space-x-4">
            <div className="h-9 w-9 bg-blue-600 rounded flex items-center justify-center font-bold text-white shadow-sm">
              CB
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-semibold text-lg tracking-tight">Consulting in a Box</span>
                <span className="bg-blue-900/60 text-blue-300 text-[10px] font-medium px-2 py-0.5 rounded border border-blue-700/50">
                  DEMO MODE: NovaMart
                </span>
              </div>
              <p className="text-xs text-corporate-400">From raw business data to actionable decisions.</p>
            </div>
          </div>

          {/* Quick-Start Workflow Stepper Banner */}
          <div className="hidden xl:flex items-center space-x-1.5 text-[11px] font-mono text-corporate-400 bg-corporate-950/80 px-3 py-1.5 rounded border border-corporate-800">
            {workflowSteps.map((step, idx) => (
              <React.Fragment key={step}>
                <span className="hover:text-blue-400 transition-colors cursor-default">{step}</span>
                {idx < workflowSteps.length - 1 && <span className="text-corporate-600">→</span>}
              </React.Fragment>
            ))}
          </div>

          {/* Actions & Demo Trigger */}
          <div className="flex items-center space-x-3">
            <button
              onClick={onRunDemo}
              disabled={demoLoading}
              className={`flex items-center space-x-2 px-3.5 py-1.5 rounded text-xs font-medium transition-all shadow-sm ${
                demoLoading
                  ? 'bg-corporate-800 text-corporate-300 cursor-not-allowed border border-corporate-700'
                  : 'bg-blue-600 hover:bg-blue-500 text-white active:scale-95'
              }`}
            >
              {demoLoading ? (
                <>
                  <Loader2 className="w-3.5 h-3.5 animate-spin text-blue-400" />
                  <span>{demoProgressStep || 'Running Analysis...'}</span>
                </>
              ) : (
                <>
                  <Play className="w-3.5 h-3.5 fill-current" />
                  <span>Try Demo (NovaMart)</span>
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Navigation Tabs Bar */}
      <div className="bg-corporate-950/90 border-t border-corporate-800/80">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex space-x-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`flex items-center space-x-2 px-4 py-2.5 text-xs font-medium border-b-2 transition-all ${
                  isActive
                    ? 'border-blue-500 text-blue-400 bg-corporate-900/50'
                    : 'border-transparent text-corporate-400 hover:text-slate-200 hover:bg-corporate-900/30'
                }`}
              >
                <Icon className={`w-3.5 h-3.5 ${isActive ? 'text-blue-400' : 'text-corporate-500'}`} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </div>
      </div>
    </header>
  );
};
