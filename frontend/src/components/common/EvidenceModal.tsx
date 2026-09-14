import React, { useState } from 'react';
import { X, Check, Copy, Terminal, Calculator, Database, ShieldCheck } from 'lucide-react';
import { EvidenceDetail } from '../../types';

interface EvidenceModalProps {
  evidence: EvidenceDetail | null;
  onClose: () => void;
}

export const EvidenceModal: React.FC<EvidenceModalProps> = ({ evidence, onClose }) => {
  const [copied, setCopied] = useState(false);

  if (!evidence) return null;

  const handleCopySql = () => {
    navigator.clipboard.writeText(evidence.sql_query);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4 sm:p-6">
      <div className="bg-white rounded-xl border border-slate-200 shadow-2xl max-w-4xl w-full max-h-[90vh] flex flex-col overflow-hidden animate-in fade-in zoom-in-95 duration-150">
        
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-200 bg-slate-50">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-blue-50 text-blue-700 rounded-lg border border-blue-200">
              <Database className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h3 className="text-base font-bold text-slate-900">{evidence.title}</h3>
                <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-semibold bg-emerald-100 text-emerald-800 border border-emerald-300">
                  <ShieldCheck className="w-3 h-3 mr-1" />
                  VERIFIED FACT
                </span>
              </div>
              <p className="text-xs text-slate-500">{evidence.methodology}</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-slate-600 p-1.5 rounded-lg hover:bg-slate-200 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content Body */}
        <div className="p-6 space-y-6 overflow-y-auto flex-1">
          
          {/* Mathematical Formula */}
          <div>
            <div className="flex items-center space-x-2 text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
              <Calculator className="w-4 h-4 text-blue-600" />
              <span>Mathematical Formula & Logic</span>
            </div>
            <div className="bg-slate-900 text-slate-100 p-3.5 rounded-lg font-mono text-xs border border-slate-800">
              <code>{evidence.mathematical_formula}</code>
            </div>
          </div>

          {/* Underlying SQL Query */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center space-x-2 text-xs font-bold text-slate-700 uppercase tracking-wider">
                <Terminal className="w-4 h-4 text-blue-600" />
                <span>Deterministic Analytical SQL Query</span>
              </div>
              <button
                onClick={handleCopySql}
                className="flex items-center space-x-1 text-xs text-slate-600 hover:text-slate-900 px-2 py-1 rounded bg-slate-100 hover:bg-slate-200 transition-colors"
              >
                {copied ? (
                  <>
                    <Check className="w-3.5 h-3.5 text-emerald-600" />
                    <span className="text-emerald-700 font-medium">Copied</span>
                  </>
                ) : (
                  <>
                    <Copy className="w-3.5 h-3.5" />
                    <span>Copy SQL</span>
                  </>
                )}
              </button>
            </div>
            <pre className="bg-slate-900 text-blue-300 p-4 rounded-lg font-mono text-xs overflow-x-auto border border-slate-800 leading-relaxed">
              <code>{evidence.sql_query}</code>
            </pre>
          </div>

          {/* Aggregated Calculation Table */}
          {evidence.aggregate_table && evidence.aggregate_table.length > 0 && (
            <div>
              <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                Period Aggregation & Variance Breakdown
              </h4>
              <div className="border border-slate-200 rounded-lg overflow-hidden">
                <table className="min-w-full divide-y divide-slate-200 text-xs text-left">
                  <thead className="bg-slate-100 font-semibold text-slate-700">
                    <tr>
                      {Object.keys(evidence.aggregate_table[0]).map((key) => (
                        <th key={key} className="px-3.5 py-2.5 uppercase tracking-wider text-[10px]">
                          {key.replace(/_/g, ' ')}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-200 bg-white">
                    {evidence.aggregate_table.map((row, idx) => (
                      <tr key={idx} className={idx % 2 === 0 ? 'bg-white' : 'bg-slate-50'}>
                        {Object.values(row).map((val: any, vIdx) => (
                          <td key={vIdx} className="px-3.5 py-2 font-mono text-slate-700">
                            {String(val)}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Sample Underlying Records */}
          {evidence.sample_records && evidence.sample_records.length > 0 && (
            <div>
              <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                Sample Record Audit Trail
              </h4>
              <div className="border border-slate-200 rounded-lg overflow-hidden">
                <table className="min-w-full divide-y divide-slate-200 text-xs text-left">
                  <thead className="bg-slate-100 font-semibold text-slate-700">
                    <tr>
                      {Object.keys(evidence.sample_records[0]).map((key) => (
                        <th key={key} className="px-3.5 py-2.5 uppercase tracking-wider text-[10px]">
                          {key.replace(/_/g, ' ')}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-200 bg-white">
                    {evidence.sample_records.map((row, idx) => (
                      <tr key={idx} className="hover:bg-blue-50/50 transition-colors">
                        {Object.values(row).map((val: any, vIdx) => (
                          <td key={vIdx} className="px-3.5 py-2 font-mono text-slate-600">
                            {String(val)}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

        </div>

        {/* Footer */}
        <div className="px-6 py-3 border-t border-slate-200 bg-slate-50 flex items-center justify-between">
          <span className="text-[11px] text-slate-500 font-mono">
            Evidence Hash: #{evidence.evidence_id} • 100% Deterministic Python/SQL Run
          </span>
          <button
            onClick={onClose}
            className="px-4 py-1.5 bg-slate-800 hover:bg-slate-900 text-white text-xs font-semibold rounded-lg transition-colors"
          >
            Close Audit View
          </button>
        </div>

      </div>
    </div>
  );
};
