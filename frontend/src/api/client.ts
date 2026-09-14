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

async function request<T>(url: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${url}`, init);
  if (!res.ok) {
    const message = await res.text().catch(() => 'Request failed');
    throw new Error(message || `Request failed (${res.status})`);
  }
  return res.json();
}

export function bootstrapDemo(): Promise<ConsultingDashboard> {
  return request<ConsultingDashboard>('/demo/bootstrap', { method: 'POST' });
}

export function getDatasetsOverview(): Promise<DatasetsOverview> {
  return request<DatasetsOverview>('/datasets/overview');
}

export async function uploadDataset(file: File): Promise<DatasetProfile> {
  const formData = new FormData();
  formData.append('file', file);
  return request<DatasetProfile>('/datasets/upload', { method: 'POST', body: formData });
}

export function getTablePreview(tableName: string): Promise<any> {
  return request<any>(`/datasets/${encodeURIComponent(tableName)}/preview`);
}

export function getConsultingCases(): Promise<ConsultingCase[]> {
  return request<ConsultingCase[]>('/analysis/cases');
}

export function generateAnalysisPlan(caseId: string, customProblem: string = ''): Promise<AnalysisPlan> {
  return request<AnalysisPlan>('/analysis/plan', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ case_id: caseId, custom_problem: customProblem })
  });
}

export function executeAnalysis(caseId: string, customProblem: string = ''): Promise<any> {
  return request<any>('/analysis/execute', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ case_id: caseId, custom_problem: customProblem })
  });
}

export function getDriverTree(): Promise<DriverNode> {
  return request<DriverNode>('/insights/tree');
}

export function getClassifiedInsights(): Promise<ExecutiveInsight[]> {
  return request<ExecutiveInsight[]>('/insights/classified');
}

export function getEvidenceDetail(evidenceId: string): Promise<EvidenceDetail> {
  return request<EvidenceDetail>(`/insights/evidence/${encodeURIComponent(evidenceId)}`);
}

export function simulateScenario(levers: ScenarioLevers): Promise<ScenarioResult> {
  return request<ScenarioResult>('/scenarios/simulate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(levers)
  });
}

export function getSensitivityMatrix(levers: ScenarioLevers = {}): Promise<any> {
  return request<any>('/scenarios/sensitivity', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(levers)
  });
}

export function getReportContent(): Promise<any> {
  return request<any>('/reports/content');
}

export function getDownloadPdfUrl(): string {
  return `${API_BASE}/reports/download-pdf`;
}

export function getSystemSettings(): Promise<any> {
  return request<any>('/settings');
}

export function updateSystemSettings(settingsData: any): Promise<any> {
  return request<any>('/settings', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(settingsData)
  });
}
