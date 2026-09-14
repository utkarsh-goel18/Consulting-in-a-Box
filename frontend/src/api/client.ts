import {
  ConsultingDashboard,
  DatasetsOverview,
  DatasetProfile,
  ConsultingCase,
  AnalysisPlan,
  DriverNode,
  ExecutiveInsight,
  EvidenceDetail,
  ScenarioLevers,
  ScenarioResult
} from '../types';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export async function bootstrapDemo(): Promise<ConsultingDashboard> {
  const res = await fetch(`${API_BASE}/demo/bootstrap`, { method: 'POST' });
  if (!res.ok) throw new Error('Failed to bootstrap demo');
  return res.json();
}

export async function getDatasetsOverview(): Promise<DatasetsOverview> {
  const res = await fetch(`${API_BASE}/datasets/overview`);
  if (!res.ok) throw new Error('Failed to fetch datasets overview');
  return res.json();
}

export async function uploadDataset(file: File): Promise<DatasetProfile> {
  const formData = new FormData();
  formData.append('file', file);
  const res = await fetch(`${API_BASE}/datasets/upload`, {
    method: 'POST',
    body: formData
  });
  if (!res.ok) throw new Error('Failed to upload dataset');
  return res.json();
}

export async function getTablePreview(tableName: string): Promise<any> {
  const res = await fetch(`${API_BASE}/datasets/${tableName}/preview`);
  if (!res.ok) throw new Error('Failed to fetch table preview');
  return res.json();
}

export async function getConsultingCases(): Promise<ConsultingCase[]> {
  const res = await fetch(`${API_BASE}/analysis/cases`);
  if (!res.ok) throw new Error('Failed to fetch consulting cases');
  return res.json();
}

export async function generateAnalysisPlan(caseId: string, customProblem: string = ''): Promise<AnalysisPlan> {
  const res = await fetch(`${API_BASE}/analysis/plan`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ case_id: caseId, custom_problem: customProblem })
  });
  if (!res.ok) throw new Error('Failed to generate analysis plan');
  return res.json();
}

export async function getDriverTree(): Promise<DriverNode> {
  const res = await fetch(`${API_BASE}/insights/tree`);
  if (!res.ok) throw new Error('Failed to fetch driver tree');
  return res.json();
}

export async function getClassifiedInsights(): Promise<ExecutiveInsight[]> {
  const res = await fetch(`${API_BASE}/insights/classified`);
  if (!res.ok) throw new Error('Failed to fetch classified insights');
  return res.json();
}

export async function getEvidenceDetail(evidenceId: string): Promise<EvidenceDetail> {
  const res = await fetch(`${API_BASE}/insights/evidence/${evidenceId}`);
  if (!res.ok) throw new Error(`Failed to fetch evidence ${evidenceId}`);
  return res.json();
}

export async function simulateScenario(levers: ScenarioLevers): Promise<ScenarioResult> {
  const res = await fetch(`${API_BASE}/scenarios/simulate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(levers)
  });
  if (!res.ok) throw new Error('Failed to run scenario simulation');
  return res.json();
}

export async function getReportContent(): Promise<any> {
  const res = await fetch(`${API_BASE}/reports/content`);
  if (!res.ok) throw new Error('Failed to fetch report content');
  return res.json();
}

export function getDownloadPdfUrl(): string {
  return `${API_BASE}/reports/download-pdf`;
}

export async function getSystemSettings(): Promise<any> {
  const res = await fetch(`${API_BASE}/settings`);
  if (!res.ok) throw new Error('Failed to fetch settings');
  return res.json();
}

export async function updateSystemSettings(settingsData: any): Promise<any> {
  const res = await fetch(`${API_BASE}/settings`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(settingsData)
  });
  if (!res.ok) throw new Error('Failed to update settings');
  return res.json();
}
