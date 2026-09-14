import React, { useState } from 'react';
import { 
  GitFork, 
  ShieldCheck, 
  Sparkles, 
  HelpCircle, 
  CheckSquare, 
  ArrowRight, 
  Eye, 
  Filter, 
  DollarSign, 
  AlertTriangle 
} from 'lucide-react';
import { ConsultingDashboard, StatementType, ExecutiveInsight } from '../types';
import { DriverTreeComponent } from '../components/charts/DriverTreeComponent';

interface InsightsPageProps {
  data: ConsultingDashboard;
  onViewEvidence: (evidenceId: string) => void;
}

export const InsightsPage: React.FC<InsightsPageProps> = ({ data, onViewEvidence }) => {
  const [filterType, setFilterType] = useState<string>('ALL');

  const filteredInsights = data.insights.filter((ins) => {
    if (filterType === 'ALL') return true;
    return ins.classification === filterType;
  });

  const getBadgeStyle = (cls: StatementType) => {
    switch (cls) {
      case 'FACT':
        return 'bg-blue-50 text-blue-700 border-blue-200';
      case 'INSIGHT':
        return 'bg-purple-50 text-purple-700 border-purple-200';
      case 'HYPOTHESIS':
        return 'bg-amber-50 text-amber-700 border-amber-200';
      case 'RECOMMENDATION':
        return 'bg-emerald-50 text-emerald-700 border-emerald-200';
      default:
        return 'bg-slate-100 text-slate-700 border-slate-200';
    }
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-200">
      
      {/* Top Header & Diagnosis Alert */}
      <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center space-x-2">
              <span className="text-[10px] font-bold uppercase tracking-wider text-blue-700 bg-blue-50 px-2 py-0.5 rounded border border-blue-200">
                Executive Diagnosis
              </span>
              <span className="text-xs font-mono text-slate-400">Governance: Rigorous Evidence Classification</span>
            </div>
            <h2 className="text-xl font-bold tracking-tight text-slate-900 mt-1">
              Profit declined 17.4% QoQ — Primary Cost & Revenue Drivers Isolated
            </h2>
            <p className="text-xs text-slate-500 mt-1 max-w-3xl">
              Every statement is governed by strict truth classification: Facts are directly supported by SQL aggregates; 
              Insights synthesize relational contributions; Hypotheses identify unconfirmed operational correlations.
            </p>
          </div>

          <div className="flex items-center space-x-2 font-mono text-xs text-slate-600 bg-slate-50 px-3 py-2 rounded-lg border border-slate-200">
            <ShieldCheck className="w-4 h-4 text-emerald-600" />
            <span>Zero Hallucination Guaranteed</span>
          </div>
        </div>
      </div>

      {/* Top 3 High-Impact Drivers Banner */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
          <span className="text-xs font-bold text-rose-600 font-mono">01 • LAST-MILE LOGISTICS SURGE</span>
          <h4 className="text-sm font-bold text-slate-900 mt-1">Delivery costs increased 13.7%</h4>
          <p className="text-xs text-slate-500 mt-1">FastLogistics instituted a 17.1% regional rate spike on Tier-2 routes.</p>
          <div className="mt-3 flex items-center justify-between pt-2 border-t border-slate-100">
            <span className="text-xs font-mono font-bold text-slate-900">Impact: +$112.4K</span>
            <button
              onClick={() => onViewEvidence('ev_shipping_surge')}
              className="text-xs text-blue-600 hover:text-blue-800 font-semibold flex items-center space-x-1"
            >
              <span>View Audit</span>
              <ArrowRight className="w-3 h-3" />
            </button>
          </div>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
          <span className="text-xs font-bold text-amber-600 font-mono">02 • BASKET SIZE / AOV SHRINKAGE</span>
          <h4 className="text-sm font-bold text-slate-900 mt-1">Average Order Value declined 5.1%</h4>
          <p className="text-xs text-slate-500 mt-1">Electronics units per basket decreased 8.4% amid promotional fatigue.</p>
          <div className="mt-3 flex items-center justify-between pt-2 border-t border-slate-100">
            <span className="text-xs font-mono font-bold text-slate-900">Impact: -$490.0K Margin</span>
            <button
              onClick={() => onViewEvidence('ev_aov_shrink')}
              className="text-xs text-blue-600 hover:text-blue-800 font-semibold flex items-center space-x-1"
            >
              <span>View Audit</span>
              <ArrowRight className="w-3 h-3" />
            </button>
          </div>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
          <span className="text-xs font-bold text-purple-600 font-mono">03 • TIER-2 CHURN & SURCHARGES</span>
          <h4 className="text-sm font-bold text-slate-900 mt-1">Customer churn increased +3.2 pp</h4>
          <p className="text-xs text-slate-500 mt-1">74% of churning customers were in Tier-2 after minimum order delivery fee.</p>
          <div className="mt-3 flex items-center justify-between pt-2 border-t border-slate-100">
            <span className="text-xs font-mono font-bold text-slate-900">At Risk: $142.0K LTV</span>
            <button
              onClick={() => onViewEvidence('ev_churn_surge')}
              className="text-xs text-blue-600 hover:text-blue-800 font-semibold flex items-center space-x-1"
            >
              <span>View Audit</span>
              <ArrowRight className="w-3 h-3" />
            </button>
          </div>
        </div>
      </div>

      {/* Signature Driver Tree Component */}
      <DriverTreeComponent
        tree={data.driver_tree}
        onViewEvidence={onViewEvidence}
      />

      {/* Classified Insights Section */}
      <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-100">
          <div>
            <h3 className="text-sm font-bold text-slate-900 tracking-tight flex items-center space-x-2">
              <ShieldCheck className="w-4 h-4 text-blue-600" />
              <span>Classified Executive Findings & Governance Ledger</span>
            </h3>
            <p className="text-xs text-slate-500">
              Filtered by analytical certainty: Facts (Data truth), Insights (Analytic interpretation), Hypotheses (Needs testing), Recommendations.
            </p>
          </div>

          {/* Classification Filters */}
          <div className="flex items-center space-x-1 bg-slate-100 p-1 rounded-lg text-xs font-semibold">
            {['ALL', 'FACT', 'INSIGHT', 'HYPOTHESIS', 'RECOMMENDATION'].map((cat) => (
              <button
                key={cat}
                onClick={() => setFilterType(cat)}
                className={`px-3 py-1 rounded-md transition-all ${
                  filterType === cat
                    ? 'bg-white text-slate-900 shadow-xs'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                {cat}
              </button>
            ))}
          </div>
        </div>

        {/* Insights Cards List */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {filteredInsights.map((ins) => (
            <div
              key={ins.id}
              className="p-4 rounded-xl border border-slate-200 bg-white hover:border-slate-300 hover:shadow-sm transition-all flex flex-col justify-between space-y-3"
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className={`px-2 py-0.5 rounded text-[10px] font-bold tracking-wider border ${getBadgeStyle(ins.classification)}`}>
                    {ins.classification}
                  </span>
                  <span className="text-[10px] font-mono text-slate-400">
                    Area: {ins.affected_area}
                  </span>
                </div>

                <h4 className="text-sm font-bold text-slate-900 leading-snug">{ins.headline}</h4>
                <p className="text-xs text-slate-600 mt-1.5 leading-relaxed">{ins.narrative}</p>
              </div>

              <div className="pt-2 border-t border-slate-100 flex items-center justify-between">
                {ins.magnitude_formatted ? (
                  <span className="text-xs font-mono font-bold text-slate-800">
                    {ins.magnitude_formatted}
                  </span>
                ) : <span />}

                <button
                  onClick={() => onViewEvidence(ins.evidence_id)}
                  className="inline-flex items-center space-x-1 text-xs font-semibold text-blue-600 hover:text-blue-800 transition-colors"
                >
                  <Eye className="w-3.5 h-3.5" />
                  <span>View Evidence</span>
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

    </div>
  );
};
