import React, { useState, useEffect } from 'react';
import { 
  Database, 
  UploadCloud, 
  FileSpreadsheet, 
  Table, 
  CheckCircle2, 
  AlertCircle, 
  Search, 
  Key, 
  Link2, 
  FileText, 
  ArrowRight,
  ShieldCheck,
  RefreshCw
} from 'lucide-react';
import { DatasetsOverview, DatasetProfile } from '../types';
import { getDatasetsOverview, uploadDataset, getTablePreview } from '../api/client';

export const DatasetsPage: React.FC = () => {
  const [overview, setOverview] = useState<DatasetsOverview | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [uploading, setUploading] = useState<boolean>(false);
  const [selectedTable, setSelectedTable] = useState<string | null>(null);
  const [tablePreview, setTablePreview] = useState<any | null>(null);
  const [previewLoading, setPreviewLoading] = useState<boolean>(false);
  const [searchQuery, setSearchQuery] = useState<string>('');

  const fetchOverview = async () => {
    try {
      setLoading(true);
      const data = await getDatasetsOverview();
      setOverview(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOverview();
  }, []);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;

    try {
      setUploading(true);
      for (let i = 0; i < files.length; i++) {
        await uploadDataset(files[i]);
      }
      await fetchOverview();
    } catch (err: any) {
      alert(`Upload error: ${err.message}`);
    } finally {
      setUploading(false);
    }
  };

  const handleInspectTable = async (tableName: string) => {
    setSelectedTable(tableName);
    try {
      setPreviewLoading(true);
      const preview = await getTablePreview(tableName);
      setTablePreview(preview);
    } catch (err) {
      console.error(err);
    } finally {
      setPreviewLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-24 space-y-3">
        <RefreshCw className="w-8 h-8 animate-spin text-blue-600" />
        <span className="text-sm font-medium text-slate-600">Profiling enterprise datasets and inferring relationships...</span>
      </div>
    );
  }

  const filteredRecords = tablePreview?.records.filter((rec: any) =>
    Object.values(rec).some((val) => String(val).toLowerCase().includes(searchQuery.toLowerCase()))
  );

  return (
    <div className="space-y-6 animate-in fade-in duration-200">
      
      {/* Header & Overall Quality Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
        <div>
          <h2 className="text-base font-bold text-slate-900 tracking-tight flex items-center space-x-2">
            <Database className="w-5 h-5 text-blue-600" />
            <span>Enterprise Data Profiling & Entity Catalog</span>
          </h2>
          <p className="text-xs text-slate-500 mt-1">
            Automated schema profiling, candidate key detection, foreign key matching, and quality scoring.
          </p>
        </div>

        <div className="flex items-center space-x-4">
          <div className="text-right">
            <span className="text-[10px] uppercase font-bold text-slate-400 block">Overall Quality Score</span>
            <span className="text-xl font-bold font-mono text-emerald-600">
              {overview?.overall_quality_score.toFixed(1)}%
            </span>
          </div>

          <label className="flex items-center space-x-2 px-3.5 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-xs font-semibold cursor-pointer shadow-sm transition-all">
            <UploadCloud className="w-4 h-4" />
            <span>{uploading ? 'Uploading...' : 'Upload CSV / XLSX'}</span>
            <input
              type="file"
              multiple
              accept=".csv,.xlsx,.xls"
              onChange={handleFileUpload}
              className="hidden"
            />
          </label>
        </div>
      </div>

      {/* Dataset Profiling Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {overview?.datasets.map((ds) => (
          <div
            key={ds.dataset_name}
            className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm hover:border-blue-300 hover:shadow-md transition-all flex flex-col justify-between"
          >
            <div>
              <div className="flex items-start justify-between">
                <div>
                  <span className="text-xs font-bold uppercase tracking-wider text-slate-900 font-mono">
                    {ds.dataset_name}
                  </span>
                  <p className="text-[11px] text-slate-400 font-mono">{ds.file_name}</p>
                </div>
                <span className={`px-2 py-0.5 rounded text-[11px] font-bold ${
                  ds.data_quality_score >= 90
                    ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                    : 'bg-amber-50 text-amber-700 border border-amber-200'
                }`}>
                  Quality {ds.data_quality_score}%
                </span>
              </div>

              {/* Rows & Columns */}
              <div className="grid grid-cols-2 gap-2 my-3 p-2.5 bg-slate-50 rounded-lg border border-slate-100 font-mono text-xs">
                <div>
                  <span className="text-[10px] text-slate-400 uppercase font-sans font-semibold">Row Count</span>
                  <div className="font-bold text-slate-900">{ds.row_count.toLocaleString()}</div>
                </div>
                <div>
                  <span className="text-[10px] text-slate-400 uppercase font-sans font-semibold">Columns</span>
                  <div className="font-bold text-slate-900">{ds.column_count}</div>
                </div>
              </div>

              {/* Primary Key Detection */}
              <div className="space-y-1 mb-3">
                <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider flex items-center space-x-1">
                  <Key className="w-3 h-3 text-amber-500" />
                  <span>Detected Primary Key(s):</span>
                </span>
                <div className="flex flex-wrap gap-1">
                  {ds.likely_primary_keys && ds.likely_primary_keys.length > 0 ? (
                    ds.likely_primary_keys.map((pk, pkIndex) => (
                      <span key={`${pk}-${pkIndex}`} className="text-[11px] font-mono bg-amber-50 text-amber-800 px-2 py-0.5 rounded border border-amber-200">
                        {pk}
                      </span>
                    ))
                  ) : (
                    <span className="text-[11px] text-slate-400 italic">Composite / Heuristic</span>
                  )}
                </div>
              </div>

              {/* Sample Columns */}
              <div>
                <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block mb-1">
                  Schema Attributes:
                </span>
                <div className="flex flex-wrap gap-1">
                  {ds.columns.slice(0, 5).map((col, colIndex) => (
                    <span key={`${col.name}-${colIndex}`} className="text-[10px] font-mono bg-slate-100 text-slate-700 px-1.5 py-0.5 rounded">
                      {col.name}
                    </span>
                  ))}
                  {ds.columns.length > 5 && (
                    <span className="text-[10px] font-mono text-slate-400 self-center">
                      +{ds.columns.length - 5} more
                    </span>
                  )}
                </div>
              </div>
            </div>

            <button
              onClick={() => handleInspectTable(ds.dataset_name)}
              className="mt-4 w-full py-2 bg-slate-100 hover:bg-slate-200 text-slate-800 rounded-lg text-xs font-semibold flex items-center justify-center space-x-1.5 transition-colors"
            >
              <span>Inspect Raw Records</span>
              <ArrowRight className="w-3.5 h-3.5 text-slate-500" />
            </button>
          </div>
        ))}
      </div>

      {/* Detected Entity Relationships Matrix */}
      <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-sm font-bold text-slate-900 tracking-tight flex items-center space-x-2">
              <Link2 className="w-4 h-4 text-blue-600" />
              <span>Inferred Entity-Relationship Model (FK Linkages)</span>
            </h3>
            <p className="text-xs text-slate-500">
              Heuristic relationship detection matching column keys and value domain intersections.
            </p>
          </div>
          <span className="text-[11px] font-mono text-slate-400 bg-slate-100 px-2 py-0.5 rounded">
            {overview?.relationships.length} links discovered
          </span>
        </div>

        <div className="border border-slate-200 rounded-lg overflow-hidden">
          <table className="min-w-full divide-y divide-slate-200 text-xs text-left">
            <thead className="bg-slate-50 text-slate-700 font-semibold font-mono">
              <tr>
                <th className="px-4 py-2.5">Source Dataset</th>
                <th className="px-4 py-2.5">Foreign Key Column</th>
                <th className="px-4 py-2.5">Target Dataset</th>
                <th className="px-4 py-2.5">Primary Key Column</th>
                <th className="px-4 py-2.5">Cardinality</th>
                <th className="px-4 py-2.5">Match Rate</th>
                <th className="px-4 py-2.5">Confidence</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200 bg-white">
              {overview?.relationships.map((rel, idx) => (
                <tr key={idx} className="hover:bg-slate-50 transition-colors">
                  <td className="px-4 py-2.5 font-bold text-slate-900">{rel.source_dataset}</td>
                  <td className="px-4 py-2.5 font-mono text-blue-700 font-semibold">{rel.source_column}</td>
                  <td className="px-4 py-2.5 font-bold text-slate-900">{rel.target_dataset}</td>
                  <td className="px-4 py-2.5 font-mono text-amber-700 font-semibold">{rel.target_column}</td>
                  <td className="px-4 py-2.5 font-mono text-slate-600">{rel.relationship_type}</td>
                  <td className="px-4 py-2.5 font-mono font-semibold text-emerald-600">{rel.match_rate_pct}%</td>
                  <td className="px-4 py-2.5">
                    <span className="text-[10px] font-semibold bg-blue-50 text-blue-700 px-2 py-0.5 rounded border border-blue-200">
                      {rel.confidence}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Raw Records Inspection Modal */}
      {selectedTable && (
        <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4 sm:p-6">
          <div className="bg-white rounded-xl border border-slate-200 shadow-2xl max-w-5xl w-full max-h-[85vh] flex flex-col overflow-hidden animate-in fade-in zoom-in-95 duration-150">
            
            <div className="flex items-center justify-between px-6 py-4 border-b border-slate-200 bg-slate-50">
              <div className="flex items-center space-x-3">
                <Table className="w-5 h-5 text-blue-600" />
                <div>
                  <h3 className="text-sm font-bold text-slate-900 font-mono">{selectedTable}.csv Preview</h3>
                  <span className="text-xs text-slate-500">First 100 sample records from ingested table</span>
                </div>
              </div>

              <div className="flex items-center space-x-3">
                <div className="relative">
                  <Search className="w-3.5 h-3.5 absolute left-2.5 top-2.5 text-slate-400" />
                  <input
                    type="text"
                    placeholder="Search in records..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-8 pr-3 py-1.5 text-xs bg-white border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-blue-500 w-52 font-mono"
                  />
                </div>
                <button
                  onClick={() => setSelectedTable(null)}
                  className="px-3 py-1.5 bg-slate-200 hover:bg-slate-300 text-slate-700 text-xs font-semibold rounded-lg"
                >
                  Close
                </button>
              </div>
            </div>

            <div className="p-4 overflow-auto flex-1">
              {previewLoading ? (
                <div className="py-16 text-center text-slate-500 text-xs">Loading table records...</div>
              ) : filteredRecords && filteredRecords.length > 0 ? (
                <table className="min-w-full divide-y divide-slate-200 text-xs text-left">
                  <thead className="bg-slate-100 font-semibold text-slate-700 font-mono sticky top-0">
                    <tr>
                      {tablePreview.columns.map((col: string, colIndex: number) => (
                        <th key={`${col}-${colIndex}`} className="px-3 py-2 uppercase text-[10px]">
                          {col}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-200 bg-white">
                    {filteredRecords.map((row: any, rIdx: number) => (
                      <tr key={rIdx} className="hover:bg-slate-50 font-mono">
                        {tablePreview.columns.map((col: string, cIdx: number) => (
                          <td key={cIdx} className="px-3 py-2 text-slate-600 whitespace-nowrap text-[11px]">
                            {String(row[col] ?? '')}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              ) : (
                <div className="py-16 text-center text-slate-500 text-xs">No records matched your search query.</div>
              )}
            </div>

          </div>
        </div>
      )}

    </div>
  );
};