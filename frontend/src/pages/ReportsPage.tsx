import React, { useState, useEffect } from 'react';
import { 
  FileText, 
  Download, 
  Printer, 
  Share2, 
  ShieldCheck, 
  CheckCircle2, 
  AlertCircle, 
  ArrowRight, 
  Clock, 
  DollarSign, 
  Layers 
} from 'lucide-react';
import { ConsultingDashboard } from '../types';
import { getDownloadPdfUrl, getReportContent } from '../api/client';

interface ReportsPageProps {
  dashboardData: ConsultingDashboard;
}

export const ReportsPage: React.FC<ReportsPageProps> = ({ dashboardData }) => {
  const [report, setReport] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    getReportContent()
      .then((data) => setReport(data))
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  const handlePrint = () => {
    window.print();
  };

  const handleDownloadPdf = () => {
    window.open(getDownloadPdfUrl(), '_blank');
  };

  const kpi = dashboardData.kpi_summary;

  return (
    <div className="space-y-6 animate-in fade-in duration-200">
      
      {/* Top Action Bar (hidden on print) */}
      <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-4 no-print">
        <div>
          <h2 className="text-base font-bold text-slate-900 tracking-tight flex items-center space-x-2">
            <FileText className="w-5 h-5 text-blue-600" />
            <span>Executive Consulting Deliverable</span>
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Formal 10-section decision intelligence report ready for CEO and board presentation.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={handlePrint}
            className="px-3.5 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg text-xs font-semibold flex items-center space-x-1.5 transition-colors"
          >
            <Printer className="w-3.5 h-3.5" />
            <span>Print View</span>
          </button>
          <button
            onClick={handleDownloadPdf}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-xs font-semibold flex items-center space-x-2 transition-all shadow-sm active:scale-95"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Download Official PDF</span>
          </button>
        </div>
      </div>

      {/* Formal Consulting Report Document Container */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-md p-8 md:p-12 max-w-5xl mx-auto space-y-10 text-slate-900 print:border-none print:shadow-none print:p-0">
        
        {/* Document Header */}
        <div className="border-b-2 border-slate-900 pb-6">
          <div className="flex justify-between items-start">
            <div>
              <span className="text-xs font-bold text-blue-600 uppercase tracking-widest font-mono">
                MANAGEMENT CONSULTING PRACTICE • DECISION INTELLIGENCE
              </span>
              <h1 className="text-2xl md:text-3xl font-extrabold text-slate-900 mt-2 tracking-tight">
                NovaMart Operating Profitability & Margin Diagnostic
              </h1>
              <p className="text-xs text-slate-500 mt-1 font-mono">
                Engagement Reference: CB-2024-Q3-0914 • Evaluation Window: {dashboardData.quarter_evaluated}
              </p>
            </div>
            <div className="text-right hidden sm:block">
              <span className="inline-flex items-center px-2.5 py-1 rounded bg-slate-100 text-slate-700 text-xs font-mono font-semibold">
                RESTRICTED / BOARD READY
              </span>
            </div>
          </div>
        </div>

        {/* Section 1: Executive Summary */}
        <section className="space-y-3">
          <h2 className="text-sm font-bold uppercase tracking-wider text-slate-900 border-l-4 border-blue-600 pl-3">
            1. Executive Summary
          </h2>
          <div className="p-4 bg-slate-50 border border-slate-200 rounded-lg text-xs text-slate-700 leading-relaxed space-y-2">
            <p>
              During Q3 2024, NovaMart experienced a <b>17.4% QoQ contraction</b> in net operating profit, falling from 
              <b>$1,280,000</b> in Q2 to <b>$1,057,260</b> in Q3. While top-line gross volume remained resilient (orders -3.3%), 
              operating margins compressed by <b>130 basis points</b> (from 12.8% to 11.5%).
            </p>
            <p>
              A systematic quantitative root cause audit decomposed this contraction into two primary structural vectors:
              (1) an uncontrolled <b>13.7% spike in last-mile delivery expenditures</b> ($112.4K excess cost, primarily localized in FastLogistics rate hikes), 
              and (2) an <b>5.1% erosion in Average Order Value (AOV)</b> coupled with <b>38.2% CAC inflation</b> in Paid Social marketing.
            </p>
            <p>
              Immediate carrier volume diversion and threshold-based shipping restructuring can recover an estimated 
              <b className="text-emerald-700"> $560,000 to $700,000 in annualized operating profit</b> with low execution complexity.
            </p>
          </div>
        </section>

        {/* Section 2: Business Problem Definition */}
        <section className="space-y-3">
          <h2 className="text-sm font-bold uppercase tracking-wider text-slate-900 border-l-4 border-blue-600 pl-3">
            2. Business Problem Definition
          </h2>
          <p className="text-xs text-slate-700 leading-relaxed">
            <b>Core Mandate:</b> Diagnose the sudden quarterly profitability erosion, isolate carrier and channel anomalies, 
            determine customer cohort defection triggers, and construct evidence-backed corrective solutions with sensitivity modeling.
          </p>
        </section>

        {/* Section 3: Strategic KPIs Scorecard */}
        <section className="space-y-3">
          <h2 className="text-sm font-bold uppercase tracking-wider text-slate-900 border-l-4 border-blue-600 pl-3">
            3. Key Performance Indicators & Financial Bridge
          </h2>
          <div className="border border-slate-200 rounded-lg overflow-hidden">
            <table className="min-w-full divide-y divide-slate-200 text-xs text-left">
              <thead className="bg-slate-900 text-white font-mono">
                <tr>
                  <th className="px-4 py-2.5">Indicator</th>
                  <th className="px-4 py-2.5">Q2 2024 Prior</th>
                  <th className="px-4 py-2.5">Q3 2024 Current</th>
                  <th className="px-4 py-2.5">Net Variance</th>
                  <th className="px-4 py-2.5">Growth Delta</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200 bg-white font-mono">
                <tr>
                  <td className="px-4 py-2 font-sans font-semibold">Net Sales Revenue</td>
                  <td className="px-4 py-2">${kpi.revenue_prior.toLocaleString()}</td>
                  <td className="px-4 py-2">${kpi.revenue_current.toLocaleString()}</td>
                  <td className="px-4 py-2 text-rose-600">-${(kpi.revenue_prior - kpi.revenue_current).toLocaleString()}</td>
                  <td className="px-4 py-2 text-rose-600">{kpi.revenue_growth_pct.toFixed(1)}%</td>
                </tr>
                <tr className="bg-slate-50">
                  <td className="px-4 py-2 font-sans font-semibold">Gross Profit</td>
                  <td className="px-4 py-2">${kpi.gross_profit_prior.toLocaleString()}</td>
                  <td className="px-4 py-2">${kpi.gross_profit_current.toLocaleString()}</td>
                  <td className="px-4 py-2 text-rose-600">-${(kpi.gross_profit_prior - kpi.gross_profit_current).toLocaleString()}</td>
                  <td className="px-4 py-2 text-rose-600">{kpi.gross_profit_growth_pct.toFixed(1)}%</td>
                </tr>
                <tr>
                  <td className="px-4 py-2 font-sans font-bold text-blue-900">Net Operating Profit</td>
                  <td className="px-4 py-2 font-bold">${kpi.net_profit_prior.toLocaleString()}</td>
                  <td className="px-4 py-2 font-bold text-rose-600">${kpi.net_profit_current.toLocaleString()}</td>
                  <td className="px-4 py-2 font-bold text-rose-600">-${(kpi.net_profit_prior - kpi.net_profit_current).toLocaleString()}</td>
                  <td className="px-4 py-2 font-bold text-rose-600">{kpi.net_profit_growth_pct.toFixed(1)}%</td>
                </tr>
                <tr className="bg-slate-50">
                  <td className="px-4 py-2 font-sans font-semibold">Operating Margin</td>
                  <td className="px-4 py-2">{kpi.net_margin_prior_pct.toFixed(1)}%</td>
                  <td className="px-4 py-2">{kpi.net_margin_current_pct.toFixed(1)}%</td>
                  <td className="px-4 py-2 text-rose-600">{kpi.net_margin_delta_pp.toFixed(1)} pp</td>
                  <td className="px-4 py-2 text-rose-600">-10.2%</td>
                </tr>
                <tr>
                  <td className="px-4 py-2 font-sans font-semibold">Average Order Value (AOV)</td>
                  <td className="px-4 py-2">${kpi.aov_prior.toFixed(2)}</td>
                  <td className="px-4 py-2">${kpi.aov_current.toFixed(2)}</td>
                  <td className="px-4 py-2 text-rose-600">-${(kpi.aov_prior - kpi.aov_current).toFixed(2)}</td>
                  <td className="px-4 py-2 text-rose-600">{kpi.aov_growth_pct.toFixed(1)}%</td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        {/* Section 4: Major Findings */}
        <section className="space-y-3">
          <h2 className="text-sm font-bold uppercase tracking-wider text-slate-900 border-l-4 border-blue-600 pl-3">
            4. Major Diagnoses & Evidence-Backed Findings
          </h2>
          <div className="space-y-2">
            {dashboardData.insights.slice(0, 4).map((ins) => (
              <div key={ins.id} className="p-3 border border-slate-200 rounded-lg text-xs flex items-start space-x-3">
                <span className={`px-2 py-0.5 rounded text-[10px] font-bold font-mono ${
                  ins.classification === 'FACT' ? 'bg-blue-100 text-blue-800' : 'bg-purple-100 text-purple-800'
                }`}>
                  [{ins.classification}]
                </span>
                <div className="flex-1">
                  <h4 className="font-bold text-slate-900">{ins.headline}</h4>
                  <p className="text-slate-600 mt-0.5 leading-relaxed">{ins.narrative}</p>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Section 5: Root Cause Analysis (Driver Tree) */}
        <section className="space-y-3">
          <h2 className="text-sm font-bold uppercase tracking-wider text-slate-900 border-l-4 border-blue-600 pl-3">
            5. Root Cause Analysis & Driver Tree Decomposition
          </h2>
          <div className="bg-slate-900 text-white p-5 rounded-lg font-mono text-xs space-y-1.5">
            <p className="font-bold text-rose-400">NET OPERATING PROFIT ↓ 17.4% (-$222,740)</p>
            <p className="text-slate-400 pl-4">├── TOTAL REVENUE ↓ 8.2% (-$820,000)</p>
            <p className="text-slate-300 pl-8">├── AOV ↓ 5.1% (-$25.34/order) [60.5% contribution to top-line drop]</p>
            <p className="text-slate-300 pl-8">└── Orders ↓ 3.3% (-660 orders)</p>
            <p className="text-slate-400 pl-4">└── TOTAL COSTS ↑ 11.7% (+$215,000)</p>
            <p className="text-rose-300 pl-8">├── Delivery Expenses ↑ 13.7% (+$112,400) [52% of total cost expansion]</p>
            <p className="text-rose-300 pl-8">├── Marketing Spend ↑ 8.2% (+$70,000) [Paid Social CAC surged +38.2%]</p>
            <p className="text-rose-300 pl-8">└── Customer Returns ↑ 6.4% (+$32,600)</p>
          </div>
        </section>

        {/* Section 6: Strategic Recommendations */}
        <section className="space-y-3">
          <h2 className="text-sm font-bold uppercase tracking-wider text-slate-900 border-l-4 border-blue-600 pl-3">
            6. Evidence-Backed Strategic Recommendations
          </h2>
          <div className="space-y-4">
            {dashboardData.recommendations.map((rec, idx) => (
              <div key={rec.id} className="p-4 border border-slate-200 rounded-lg bg-slate-50 space-y-2 text-xs">
                <div className="flex items-center justify-between">
                  <h3 className="font-bold text-sm text-slate-900">{idx + 1}. {rec.title}</h3>
                  <span className="font-mono font-bold text-emerald-700 bg-emerald-50 px-2.5 py-1 rounded border border-emerald-200">
                    Impact: {rec.expected_impact_formatted}
                  </span>
                </div>
                <p className="text-slate-700"><b>Action:</b> {rec.recommendation}</p>
                <p className="text-slate-600"><b>Data Rationale:</b> {rec.why}</p>
                <div className="pt-2 border-t border-slate-200 flex items-center justify-between text-[11px] text-slate-500 font-mono">
                  <span>Confidence: <b>{rec.confidence}</b></span>
                  <span>Timeframe: <b>{rec.implementation_timeframe}</b></span>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Section 7: Next Steps Roadmap */}
        <section className="space-y-3">
          <h2 className="text-sm font-bold uppercase tracking-wider text-slate-900 border-l-4 border-blue-600 pl-3">
            7. Governance, Implementation Roadmap & Next Steps
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
            <div className="p-3 bg-white border border-slate-200 rounded-lg">
              <span className="font-bold text-blue-600 block mb-1">Phase 1: Days 1–15</span>
              <p className="text-slate-600">Enforce contract routing caps on FastLogistics and shift Tier-2 northern volume to ExpressCargo.</p>
            </div>
            <div className="p-3 bg-white border border-slate-200 rounded-lg">
              <span className="font-bold text-blue-600 block mb-1">Phase 2: Days 16–45</span>
              <p className="text-slate-600">Cap Paid Social spend at $340K/qtr and reallocate savings to Google Intent Search and Affiliates.</p>
            </div>
            <div className="p-3 bg-white border border-slate-200 rounded-lg">
              <span className="font-bold text-blue-600 block mb-1">Phase 3: Days 46–90</span>
              <p className="text-slate-600">Implement $65 minimum free shipping threshold and measure AOV cross-sell elasticity.</p>
            </div>
          </div>
        </section>

        {/* Report Footer Sign-off */}
        <div className="pt-8 border-t border-slate-200 flex items-center justify-between text-xs text-slate-500 font-mono">
          <span>Prepared by Consulting in a Box Decision Intelligence Platform</span>
          <span>Verified via Deterministic SQL/Python Engine</span>
        </div>

      </div>

    </div>
  );
};
