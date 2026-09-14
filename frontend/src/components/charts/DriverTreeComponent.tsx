import React, { useState } from 'react';
import { 
  ArrowDownRight, 
  ArrowUpRight, 
  ChevronRight, 
  ChevronDown, 
  Layers, 
  Eye, 
  TrendingDown, 
  TrendingUp, 
  DollarSign, 
  AlertCircle 
} from 'lucide-react';
import { DriverNode } from '../../types';

interface DriverTreeComponentProps {
  tree: DriverNode;
  onViewEvidence: (evidenceId: string) => void;
}

export const DriverTreeComponent: React.FC<DriverTreeComponentProps> = ({
  tree,
  onViewEvidence,
}) => {
  const [selectedNode, setSelectedNode] = useState<DriverNode>(tree);
  const [expandedNodes, setExpandedNodes] = useState<Record<string, boolean>>({
    root_net_profit: true,
    driver_revenue: true,
    driver_costs: true,
    driver_orders: true,
  });

  const toggleExpand = (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setExpandedNodes((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  const renderTreeItem = (node: DriverNode, depth: number = 0) => {
    const isExpanded = expandedNodes[node.id] ?? true;
    const isSelected = selectedNode.id === node.id;
    const hasChildren = node.children && node.children.length > 0;
    const isNegative = node.status === 'negative';

    return (
      <div key={node.id} className="select-none">
        {/* Node Card Row */}
        <div
          onClick={() => setSelectedNode(node)}
          style={{ paddingLeft: `${depth * 24 + 12}px` }}
          className={`group flex items-center justify-between py-2.5 pr-4 rounded-lg cursor-pointer border transition-all my-1 ${
            isSelected
              ? 'bg-blue-50/80 border-blue-400 shadow-sm'
              : 'bg-white hover:bg-slate-50 border-slate-200'
          }`}
        >
          {/* Left: Expander & Label */}
          <div className="flex items-center space-x-2 min-w-0">
            {hasChildren ? (
              <button
                onClick={(e) => toggleExpand(node.id, e)}
                className="p-1 text-slate-400 hover:text-slate-700 rounded transition-colors"
              >
                {isExpanded ? (
                  <ChevronDown className="w-4 h-4" />
                ) : (
                  <ChevronRight className="w-4 h-4" />
                )}
              </button>
            ) : (
              <div className="w-6" />
            )}

            <div className="truncate">
              <div className="flex items-center space-x-2">
                <span className={`text-xs font-semibold ${isSelected ? 'text-blue-900 font-bold' : 'text-slate-800'}`}>
                  {node.label}
                </span>
                {node.evidence_id && (
                  <span className="text-[10px] text-blue-600 font-mono bg-blue-100/60 px-1.5 py-0.2 rounded">
                    audit
                  </span>
                )}
              </div>
              <p className="text-[11px] text-slate-400 font-mono">
                {node.currency}{node.current_value.toLocaleString()} (prior: {node.currency}{node.prior_value.toLocaleString()})
              </p>
            </div>
          </div>

          {/* Right: Variance Badge & Contribution */}
          <div className="flex items-center space-x-3 shrink-0">
            {/* Contribution Bar */}
            {node.contribution_pct > 0 && depth > 0 && (
              <div className="hidden sm:flex flex-col items-end text-[10px] font-mono text-slate-500">
                <span>{node.contribution_pct.toFixed(1)}% of parent</span>
                <div className="w-14 bg-slate-100 h-1.5 rounded-full overflow-hidden mt-0.5">
                  <div
                    className={`h-full ${isNegative ? 'bg-rose-500' : 'bg-emerald-500'}`}
                    style={{ width: `${Math.min(node.contribution_pct, 100)}%` }}
                  />
                </div>
              </div>
            )}

            {/* Delta Badge */}
            <div
              className={`flex items-center space-x-1 px-2 py-0.5 rounded text-xs font-semibold ${
                isNegative
                  ? 'bg-rose-50 text-rose-700 border border-rose-200'
                  : 'bg-emerald-50 text-emerald-700 border border-emerald-200'
              }`}
            >
              {node.trend === 'down' ? (
                <ArrowDownRight className="w-3.5 h-3.5" />
              ) : (
                <ArrowUpRight className="w-3.5 h-3.5" />
              )}
              <span>
                {node.delta_pct > 0 ? '+' : ''}
                {node.delta_pct.toFixed(1)}%
              </span>
            </div>
          </div>
        </div>

        {/* Child Subtree */}
        {hasChildren && isExpanded && (
          <div className="border-l-2 border-slate-200 ml-5 my-0.5">
            {node.children.map((child) => renderTreeItem(child, depth + 1))}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
      {/* Driver Tree Interactive Hierarchy */}
      <div className="lg:col-span-7 bg-white rounded-xl border border-slate-200 p-5 shadow-sm">
        <div className="flex items-center justify-between pb-3 mb-3 border-b border-slate-100">
          <div>
            <h3 className="text-sm font-bold text-slate-900 tracking-tight flex items-center space-x-2">
              <Layers className="w-4 h-4 text-blue-600" />
              <span>Hierarchical Root Cause Tree</span>
            </h3>
            <p className="text-xs text-slate-500">
              Click any driver node to inspect financial impact, affected segments, and audit evidence.
            </p>
          </div>
          <span className="text-[11px] font-mono text-slate-400 bg-slate-100 px-2 py-1 rounded">
            Decomposition Model
          </span>
        </div>

        <div className="space-y-1">
          {renderTreeItem(tree, 0)}
        </div>
      </div>

      {/* Selected Driver Inspection Drawer */}
      <div className="lg:col-span-5 bg-white rounded-xl border border-slate-200 p-5 shadow-sm sticky top-24">
        <div className="pb-3 mb-4 border-b border-slate-100">
          <span className="text-[10px] font-bold uppercase tracking-wider text-blue-600 bg-blue-50 px-2 py-0.5 rounded border border-blue-200">
            Selected Driver Inspection
          </span>
          <h4 className="text-lg font-bold text-slate-900 mt-2">{selectedNode.label}</h4>
          <p className="text-xs text-slate-500">Metric Key: <span className="font-mono text-slate-700">{selectedNode.metric_name}</span></p>
        </div>

        <div className="space-y-4">
          {/* Key Metrics Grid */}
          <div className="grid grid-cols-2 gap-3">
            <div className="bg-slate-50 p-3 rounded-lg border border-slate-200">
              <span className="text-[10px] font-semibold text-slate-500 uppercase">Quarterly Delta</span>
              <div className="text-base font-bold text-slate-900 mt-0.5">
                {selectedNode.delta_pct > 0 ? '+' : ''}{selectedNode.delta_pct.toFixed(1)}%
              </div>
              <span className="text-[10px] text-slate-400 font-mono">
                {selectedNode.currency}{Math.abs(selectedNode.delta_value).toLocaleString()} absolute
              </span>
            </div>

            <div className="bg-slate-50 p-3 rounded-lg border border-slate-200">
              <span className="text-[10px] font-semibold text-slate-500 uppercase">Impact Sizing</span>
              <div className="text-base font-bold text-slate-900 mt-0.5">
                {selectedNode.currency}{selectedNode.impact_magnitude.toLocaleString()}
              </div>
              <span className="text-[10px] text-slate-400 font-mono">
                {selectedNode.contribution_pct.toFixed(1)}% contribution
              </span>
            </div>
          </div>

          {/* Affected Segments & Risk Areas */}
          {selectedNode.affected_segments && selectedNode.affected_segments.length > 0 && (
            <div>
              <span className="text-xs font-bold text-slate-700 uppercase tracking-wider block mb-2">
                Primary Affected Segments & Partners
              </span>
              <div className="space-y-1.5">
                {selectedNode.affected_segments.map((seg, idx) => (
                  <div key={idx} className="flex items-center space-x-2 text-xs text-slate-700 bg-slate-50 px-3 py-1.5 rounded border border-slate-200">
                    <AlertCircle className="w-3.5 h-3.5 text-amber-500 shrink-0" />
                    <span className="font-medium">{seg}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Mathematical Rationale */}
          <div className="p-3 bg-blue-50/50 rounded-lg border border-blue-100 text-xs text-slate-600 leading-relaxed">
            <span className="font-semibold text-blue-900 block mb-1">Diagnostic Context:</span>
            Variance in <span className="font-medium text-slate-800">{selectedNode.label}</span> directly accounted for{' '}
            <span className="font-bold text-blue-800">{selectedNode.contribution_pct.toFixed(1)}%</span> of total parent variance. 
            Root cause analysis identifies concentration in specific operational vendors and pricing tier degradation.
          </div>

          {/* Audit Evidence Action */}
          {selectedNode.evidence_id && (
            <button
              onClick={() => onViewEvidence(selectedNode.evidence_id!)}
              className="w-full flex items-center justify-center space-x-2 px-4 py-2.5 bg-slate-900 hover:bg-slate-800 text-white rounded-lg text-xs font-semibold transition-colors shadow-sm"
            >
              <Eye className="w-4 h-4 text-blue-400" />
              <span>View Underlying Evidence & SQL Audit Trail</span>
            </button>
          )}

        </div>
      </div>
    </div>
  );
};
