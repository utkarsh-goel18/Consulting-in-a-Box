import React, { useState, useEffect } from 'react';
import { 
  Compass, 
  TrendingDown, 
  Users, 
  BarChart3, 
  DollarSign, 
  Target, 
  ShoppingBag, 
  Package, 
  Activity, 
  ArrowRight, 
  CheckCircle2, 
  Clock, 
  Sparkles, 
  Play, 
  FileText 
} from 'lucide-react';
import { ConsultingCase, AnalysisPlan } from '../types';
import { getConsultingCases, generateAnalysisPlan } from '../api/client';

interface AnalysisPageProps {
  onPlanExecuted: () => void;
}

export const AnalysisPage: React.FC<AnalysisPageProps> = ({ onPlanExecuted }) => {
  const [cases, setCases] = useState<ConsultingCase[]>([]);
  const [selectedCaseId, setSelectedCaseId] = useState<string>('case_profitability_decline');
  const [customProblem, setCustomProblem] = useState<string>('');
  const [plan, setPlan] = useState<AnalysisPlan | null>(null);
  const [planning, setPlanning] = useState<boolean>(false);
  const [executing, setExecuting] = useState<boolean>(false);

  useEffect(() => {
    getConsultingCases()
      .then((data) => {
        setCases(data);
        // Default plan generation for first case
        handleGeneratePlan('case_profitability_decline', '');
      })
      .catch((err) => console.error(err));
  }, []);

  const handleGeneratePlan = async (caseId: string, customText: string) => {
    try {
      setPlanning(true);
      const generatedPlan = await generateAnalysisPlan(caseId, customText);
      setPlan(generatedPlan);
    } catch (err) {
      console.error(err);
    } finally {
      setPlanning(false);
    }
  };

  const handleCaseSelect = (cId: string) => {
    setSelectedCaseId(cId);
    setCustomProblem('');
    handleGeneratePlan(cId, '');
  };

  const handleCustomSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!customProblem.trim()) return;
    setSelectedCaseId('custom');
    handleGeneratePlan('custom', customProblem);
  };

  const handleExecute = () => {
    setExecuting(true);
    setTimeout(() => {
      setExecuting(false);
      onPlanExecuted();
    }, 1000);
  };

  const getIcon = (iconName: string) => {
    switch (iconName) {
      case 'TrendingDown': return <TrendingDown className="w-4 h-4" />;
      case 'Users': return <Users className="w-4 h-4" />;
      case 'BarChart3': return <BarChart3 className="w-4 h-4" />;
      case 'DollarSign': return <DollarSign className="w-4 h-4" />;
      case 'Target': return <Target className="w-4 h-4" />;
      case 'ShoppingBag': return <ShoppingBag className="w-4 h-4" />;
      case 'Package': return <Package className="w-4 h-4" />;
      default: return <Activity className="w-4 h-4" />;
    }
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-200">
      
      {/* Header */}
      <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
        <h2 className="text-base font-bold text-slate-900 tracking-tight flex items-center space-x-2">
          <Compass className="w-5 h-5 text-blue-600" />
          <span>Strategic Problem Selection & Analysis Plan Engine</span>
        </h2>
        <p className="text-xs text-slate-500 mt-1">
          Select a standard management consulting engagement or describe an ad-hoc operational problem. 
          The AI formulates a structured quantitative plan executed deterministically by the Python/SQL engine.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        
        {/* Left: 8 Predefined Cases & Custom Input */}
        <div className="lg:col-span-5 space-y-4">
          <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-3">
              Standard Consulting Engagements
            </h3>
            
            <div className="space-y-2">
              {cases.map((c) => {
                const isSelected = selectedCaseId === c.id;
                return (
                  <button
                    key={c.id}
                    onClick={() => handleCaseSelect(c.id)}
                    className={`w-full text-left p-3 rounded-lg border transition-all flex items-start space-x-3 ${
                      isSelected
                        ? 'bg-blue-50/80 border-blue-400 shadow-sm'
                        : 'bg-white hover:bg-slate-50 border-slate-200'
                    }`}
                  >
                    <div className={`p-2 rounded-lg mt-0.5 ${
                      isSelected ? 'bg-blue-600 text-white' : 'bg-slate-100 text-slate-600'
                    }`}>
                      {getIcon(c.icon)}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between">
                        <span className={`text-xs font-bold ${isSelected ? 'text-blue-900' : 'text-slate-900'}`}>
                          {c.title}
                        </span>
                        <span className="text-[10px] text-slate-400 font-medium">{c.category}</span>
                      </div>
                      <p className="text-[11px] text-slate-500 line-clamp-2 mt-1 leading-snug">
                        {c.default_question}
                      </p>
                    </div>
                  </button>
                );
              })}
            </div>

            {/* Custom Problem Input Form */}
            <div className="mt-5 pt-4 border-t border-slate-100">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-700 block mb-2">
                Describe Your Own Business Problem
              </span>
              <form onSubmit={handleCustomSubmit} className="space-y-2">
                <textarea
                  rows={2}
                  placeholder="e.g. Our profit declined significantly this quarter. Find the major drivers across logistics and pricing."
                  value={customProblem}
                  onChange={(e) => setCustomProblem(e.target.value)}
                  className="w-full p-2.5 text-xs bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-blue-500 font-sans"
                />
                <button
                  type="submit"
                  disabled={!customProblem.trim() || planning}
                  className="w-full py-2 bg-slate-900 hover:bg-slate-800 disabled:opacity-50 text-white rounded-lg text-xs font-semibold flex items-center justify-center space-x-2 transition-colors"
                >
                  <Sparkles className="w-3.5 h-3.5 text-blue-400" />
                  <span>Generate Custom Plan</span>
                </button>
              </form>
            </div>

          </div>
        </div>

        {/* Right: Generated Analysis Plan & Execution */}
        <div className="lg:col-span-7 bg-white p-5 rounded-xl border border-slate-200 shadow-sm space-y-5">
          {planning ? (
            <div className="py-24 text-center text-slate-500 text-xs">
              <Clock className="w-6 h-6 animate-spin mx-auto text-blue-600 mb-2" />
              <span>Synthesizing structured consulting analysis plan...</span>
            </div>
          ) : plan ? (
            <>
              {/* Plan Header */}
              <div className="flex items-start justify-between pb-3 border-b border-slate-100">
                <div>
                  <span className="text-[10px] font-bold uppercase tracking-wider text-blue-600 bg-blue-50 px-2 py-0.5 rounded border border-blue-200">
                    Analysis Plan: {plan.case_id}
                  </span>
                  <h3 className="text-base font-bold text-slate-900 mt-1">{plan.case_title}</h3>
                  <p className="text-xs text-slate-500 mt-0.5">Focus: {plan.business_question}</p>
                </div>
                <button
                  onClick={handleExecute}
                  disabled={executing}
                  className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold rounded-lg flex items-center space-x-2 transition-all shadow-sm active:scale-95"
                >
                  <Play className="w-3.5 h-3.5 fill-current" />
                  <span>{executing ? 'Computing Results...' : 'Execute Deterministic Analysis'}</span>
                </button>
              </div>

              {/* Execution Steps List */}
              <div className="space-y-3">
                {plan.steps.map((step) => (
                  <div
                    key={step.step_number}
                    className="p-3.5 bg-slate-50 rounded-lg border border-slate-200 flex items-start space-x-3 hover:border-slate-300 transition-colors"
                  >
                    <div className="w-6 h-6 rounded-full bg-blue-100 text-blue-800 flex items-center justify-center font-bold text-xs shrink-0 mt-0.5">
                      {step.step_number}
                    </div>

                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-bold text-slate-900">{step.title}</span>
                        <span className="text-[10px] font-mono bg-white text-slate-600 px-2 py-0.5 rounded border border-slate-200">
                          {step.method}
                        </span>
                      </div>
                      <p className="text-xs text-slate-600 mt-1 leading-relaxed">{step.description}</p>
                      
                      {/* Target Metrics */}
                      <div className="flex items-center space-x-1.5 mt-2">
                        <span className="text-[10px] text-slate-400 font-semibold uppercase">Target Metrics:</span>
                        {step.target_metrics.map((tm) => (
                          <span key={tm} className="text-[10px] font-mono bg-blue-50 text-blue-700 px-1.5 py-0.2 rounded">
                            {tm}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              {/* Governance Note */}
              <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-lg flex items-center space-x-2 text-xs text-emerald-800">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                <span>
                  Execution Protocol: All steps are executed via compiled SQL queries and deterministic NumPy/Pandas functions. No numerical hallucination permitted.
                </span>
              </div>
            </>
          ) : null}
        </div>

      </div>

    </div>
  );
};
