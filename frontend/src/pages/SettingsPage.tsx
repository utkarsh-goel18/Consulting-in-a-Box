import React, { useState, useEffect } from 'react';
import { 
  Settings as SettingsIcon, 
  Database, 
  Cpu, 
  ShieldCheck, 
  Check, 
  RefreshCw, 
  Server, 
  Key 
} from 'lucide-react';
import { getSystemSettings, updateSystemSettings } from '../api/client';

export const SettingsPage: React.FC = () => {
  const [settings, setSettings] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [saving, setSaving] = useState<boolean>(false);
  const [savedSuccess, setSavedSuccess] = useState<boolean>(false);

  const [aiProvider, setAiProvider] = useState<string>('mock');
  const [geminiKey, setGeminiKey] = useState<string>('');
  const [openaiKey, setOpenaiKey] = useState<string>('');
  const [databaseUrl, setDatabaseUrl] = useState<string>('');
  const [demoMode, setDemoMode] = useState<boolean>(true);

  useEffect(() => {
    getSystemSettings()
      .then((data) => {
        setSettings(data);
        setAiProvider(data.ai_provider || 'mock');
        setDemoMode(data.demo_mode ?? true);
      })
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setSaving(true);
      await updateSystemSettings({
        ai_provider: aiProvider,
        gemini_api_key: geminiKey,
        openai_api_key: openaiKey,
        database_url: databaseUrl || undefined,
        demo_mode: demoMode
      });
      setSavedSuccess(true);
      setTimeout(() => setSavedSuccess(false), 2500);
      const updated = await getSystemSettings();
      setSettings(updated);
    } catch (err: any) {
      alert(`Failed to save settings: ${err.message}`);
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="py-24 text-center text-slate-500 text-xs">
        <RefreshCw className="w-6 h-6 animate-spin mx-auto text-blue-600 mb-2" />
        <span>Loading system and data engine settings...</span>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6 animate-in fade-in duration-200">
      
      {/* Header */}
      <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
        <h2 className="text-base font-bold text-slate-900 tracking-tight flex items-center space-x-2">
          <SettingsIcon className="w-5 h-5 text-blue-600" />
          <span>Platform Infrastructure & Intelligence Settings</span>
        </h2>
        <p className="text-xs text-slate-500 mt-1">
          Configure analytical database connectivity, AI reasoning provider, and demo sandbox mode.
        </p>
      </div>

      <form onSubmit={handleSave} className="space-y-6">
        
        {/* Database & Storage Architecture */}
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-slate-100">
            <div className="flex items-center space-x-2">
              <Database className="w-4 h-4 text-blue-600" />
              <h3 className="text-sm font-bold text-slate-900">Database & Analytical OLAP Engine</h3>
            </div>
            <span className="text-[10px] font-mono text-slate-500 bg-slate-100 px-2 py-0.5 rounded">
              DuckDB + PostgreSQL Dual Mode
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
            <div className="p-3 bg-slate-50 border border-slate-200 rounded-lg">
              <span className="font-bold text-slate-700 block mb-1">In-Process OLAP Engine:</span>
              <p className="text-slate-600 font-mono text-[11px]">DuckDB In-Memory OLAP (Active)</p>
              <span className="text-[10px] text-emerald-600 font-semibold block mt-1">
                ✓ Ready for sub-second analytical queries
              </span>
            </div>

            <div className="p-3 bg-slate-50 border border-slate-200 rounded-lg">
              <span className="font-bold text-slate-700 block mb-1">PostgreSQL Enterprise Status:</span>
              <p className="text-slate-600 font-mono text-[11px]">
                {settings?.postgres_status?.connected ? 'Connected' : 'Disconnected / Standby'}
              </p>
              <span className="text-[10px] text-slate-500 block mt-1">
                {settings?.postgres_status?.version || 'Local instance ready. Configurable below.'}
              </span>
            </div>
          </div>

          <div>
            <label className="block text-xs font-bold text-slate-700 mb-1">
              Enterprise PostgreSQL Connection URL (Optional)
            </label>
            <input
              type="text"
              placeholder="postgresql://user:password@localhost:5432/consulting_box"
              value={databaseUrl}
              onChange={(e) => setDatabaseUrl(e.target.value)}
              className="w-full p-2.5 text-xs bg-slate-50 border border-slate-200 rounded-lg font-mono focus:outline-none focus:ring-1 focus:ring-blue-500"
            />
            <span className="text-[10px] text-slate-400 mt-1 block">
              Leave blank to operate using embedded DuckDB high-performance analytics.
            </span>
          </div>
        </div>

        {/* AI Abstraction Layer */}
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-slate-100">
            <div className="flex items-center space-x-2">
              <Cpu className="w-4 h-4 text-blue-600" />
              <h3 className="text-sm font-bold text-slate-900">AI Provider & Reasoning Engine</h3>
            </div>
            <span className="text-[10px] font-mono text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
              Deterministic Guardrails Active
            </span>
          </div>

          <div className="space-y-3">
            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1.5">
                Active Intelligence Provider
              </label>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <button
                  type="button"
                  onClick={() => setAiProvider('mock')}
                  className={`p-3 rounded-lg border text-left text-xs transition-all ${
                    aiProvider === 'mock'
                      ? 'border-blue-600 bg-blue-50/50 shadow-xs'
                      : 'border-slate-200 hover:bg-slate-50'
                  }`}
                >
                  <span className="font-bold text-slate-900 block">Mock Strategic Consultant</span>
                  <span className="text-[11px] text-slate-500">Deterministic, zero-key offline mode</span>
                </button>

                <button
                  type="button"
                  onClick={() => setAiProvider('gemini')}
                  className={`p-3 rounded-lg border text-left text-xs transition-all ${
                    aiProvider === 'gemini'
                      ? 'border-blue-600 bg-blue-50/50 shadow-xs'
                      : 'border-slate-200 hover:bg-slate-50'
                  }`}
                >
                  <span className="font-bold text-slate-900 block">Google Gemini</span>
                  <span className="text-[11px] text-slate-500">Gemini 1.5 Flash / Pro reasoning</span>
                </button>

                <button
                  type="button"
                  onClick={() => setAiProvider('openai')}
                  className={`p-3 rounded-lg border text-left text-xs transition-all ${
                    aiProvider === 'openai'
                      ? 'border-blue-600 bg-blue-50/50 shadow-xs'
                      : 'border-slate-200 hover:bg-slate-50'
                  }`}
                >
                  <span className="font-bold text-slate-900 block">OpenAI GPT-4o</span>
                  <span className="text-[11px] text-slate-500">OpenAI compatible API</span>
                </button>
              </div>
            </div>

            {aiProvider === 'gemini' && (
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">
                  Google Gemini API Key
                </label>
                <input
                  type="password"
                  placeholder="AIzaSy..."
                  value={geminiKey}
                  onChange={(e) => setGeminiKey(e.target.value)}
                  className="w-full p-2.5 text-xs bg-slate-50 border border-slate-200 rounded-lg font-mono focus:outline-none focus:ring-1 focus:ring-blue-500"
                />
              </div>
            )}

            {aiProvider === 'openai' && (
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">
                  OpenAI API Key
                </label>
                <input
                  type="password"
                  placeholder="sk-..."
                  value={openaiKey}
                  onChange={(e) => setOpenaiKey(e.target.value)}
                  className="w-full p-2.5 text-xs bg-slate-50 border border-slate-200 rounded-lg font-mono focus:outline-none focus:ring-1 focus:ring-blue-500"
                />
              </div>
            )}
          </div>
        </div>

        {/* Save Bar */}
        <div className="flex items-center justify-between bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
          <div className="flex items-center space-x-2 text-xs text-slate-600">
            <ShieldCheck className="w-4 h-4 text-emerald-600" />
            <span>Settings are preserved in application memory and environment.</span>
          </div>

          <button
            type="submit"
            disabled={saving}
            className="px-5 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-xs font-semibold flex items-center space-x-2 transition-all shadow-sm active:scale-95"
          >
            {saving ? (
              <span>Saving...</span>
            ) : savedSuccess ? (
              <>
                <Check className="w-4 h-4 text-white" />
                <span>Saved Successfully</span>
              </>
            ) : (
              <span>Save Configuration</span>
            )}
          </button>
        </div>

      </form>

    </div>
  );
};
