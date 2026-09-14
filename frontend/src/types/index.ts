export type StatementType = 'FACT' | 'INSIGHT' | 'HYPOTHESIS' | 'RECOMMENDATION';

export type ColumnType = 'NUMERIC' | 'CATEGORICAL' | 'DATETIME' | 'TEXT' | 'BOOLEAN' | 'ID';

export interface ColumnProfile {
  name: string;
  dtype: ColumnType;
  raw_dtype: string;
  total_count: number;
  missing_count: number;
  missing_pct: number;
  unique_count: number;
  is_unique: boolean;
  sample_values: string[];
  min_val?: number | null;
  max_val?: number | null;
  mean_val?: number | null;
}

export interface DatasetProfile {
  dataset_name: string;
  file_name: string;
  row_count: number;
  column_count: number;
  data_quality_score: number;
  likely_primary_keys: string[];
  columns: ColumnProfile[];
  file_size_bytes: number;
}

export interface DetectedRelationship {
  source_dataset: string;
  source_column: string;
  target_dataset: string;
  target_column: string;
  relationship_type: string;
  match_rate_pct: number;
  confidence: 'High' | 'Medium' | 'Low';
}

export interface DatasetsOverview {
  datasets: DatasetProfile[];
  relationships: DetectedRelationship[];
  overall_quality_score: number;
}

export interface KPISummary {
  revenue_prior: number;
  revenue_current: number;
  revenue_growth_pct: number;
  gross_profit_prior: number;
  gross_profit_current: number;
  gross_profit_growth_pct: number;
  net_profit_prior: number;
  net_profit_current: number;
  net_profit_growth_pct: number;
  net_margin_prior_pct: number;
  net_margin_current_pct: number;
  net_margin_delta_pp: number;
  orders_prior: number;
  orders_current: number;
  orders_growth_pct: number;
  aov_prior: number;
  aov_current: number;
  aov_growth_pct: number;
  active_customers_prior: number;
  active_customers_current: number;
  active_customers_growth_pct: number;
  cac_prior: number;
  cac_current: number;
  cac_growth_pct: number;
  churn_rate_prior_pct: number;
  churn_rate_current_pct: number;
  churn_rate_delta_pp: number;
  currency_symbol: string;
}

export interface DriverNode {
  id: string;
  label: string;
  metric_name: string;
  prior_value: number;
  current_value: number;
  delta_value: number;
  delta_pct: number;
  contribution_pct: number;
  impact_magnitude: number;
  currency: string;
  trend: 'up' | 'down' | 'flat';
  status: 'positive' | 'negative' | 'neutral';
  affected_segments: string[];
  children: DriverNode[];
  evidence_id?: string | null;
}

export interface EvidenceDetail {
  evidence_id: string;
  title: string;
  methodology: string;
  mathematical_formula: string;
  sql_query: string;
  sample_records: Record<string, any>[];
  aggregate_table: Record<string, any>[];
}

export interface ExecutiveInsight {
  id: string;
  classification: StatementType;
  headline: string;
  narrative: string;
  magnitude_value?: number | null;
  magnitude_formatted?: string | null;
  affected_area: string;
  confidence: 'High' | 'Medium' | 'Low';
  evidence_id: string;
}

export interface ScenarioLevers {
  price_change_pct: number;
  marketing_spend_delta_pct: number;
  churn_rate_delta_pp: number;
  delivery_cost_delta_pct: number;
  cogs_reduction_pct: number;
  return_rate_delta_pp: number;
}

export interface MetricComparison {
  metric_name: string;
  base_value: number;
  scenario_value: number;
  absolute_delta: number;
  percentage_delta: number;
  formatted_base: string;
  formatted_scenario: string;
  formatted_delta: string;
  is_positive_trend: boolean;
}

export interface ScenarioResult {
  levers: ScenarioLevers;
  metrics: Record<string, MetricComparison>;
  waterfall_breakdown: Array<{ lever: string; amount: number; type: string }>;
  executive_verdict: string;
  key_assumptions: string[];
}

export interface StrategicRecommendation {
  id: string;
  title: string;
  recommendation: string;
  why: string;
  expected_impact_annualized: number;
  expected_impact_formatted: string;
  confidence: string;
  implementation_timeframe: string;
  assumptions: string[];
  supporting_evidence_ids: string[];
}

export interface ConsultingDashboard {
  company_name: string;
  industry: string;
  quarter_evaluated: string;
  problem_title: string;
  kpi_summary: KPISummary;
  driver_tree: DriverNode;
  insights: ExecutiveInsight[];
  recommendations: StrategicRecommendation[];
  p_and_l_waterfall: Array<{ step: string; amount: number; type: string; running_total: number }>;
  monthly_trend: Array<{ month: string; revenue: number; orders: number }>;
  category_performance: Array<{ category: string; revenue: number; gross_margin: number; margin_pct: number; pareto_pct: number; trend: string }>;
  marketing_efficiency: Array<{ channel: string; spend: number; cac: number; cac_growth_pct: number; roas: number; verdict: string }>;
  shipping_partner_breakdown: Array<{ partner: string; q2_avg_cost: number; q3_avg_cost: number; delta_pct: number; orders: number; excess_cost: number }>;
}

export interface AnalysisStep {
  step_number: number;
  title: string;
  method: string;
  description: string;
  target_metrics: string[];
  status: string;
}

export interface AnalysisPlan {
  case_id: string;
  case_title: string;
  business_question: string;
  steps: AnalysisStep[];
  estimated_impact_area: string;
}

export interface ConsultingCase {
  id: string;
  title: string;
  category: string;
  default_question: string;
  icon: string;
}
