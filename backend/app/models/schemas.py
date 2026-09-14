from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from enum import Enum

class StatementType(str, Enum):
    FACT = "FACT"
    INSIGHT = "INSIGHT"
    HYPOTHESIS = "HYPOTHESIS"
    RECOMMENDATION = "RECOMMENDATION"

class ColumnType(str, Enum):
    NUMERIC = "NUMERIC"
    CATEGORICAL = "CATEGORICAL"
    DATETIME = "DATETIME"
    TEXT = "TEXT"
    BOOLEAN = "BOOLEAN"
    ID = "ID"

# 1. Dataset Profiling Schemas
class ColumnProfile(BaseModel):
    name: str
    dtype: ColumnType
    raw_dtype: str
    total_count: int
    missing_count: int
    missing_pct: float
    unique_count: int
    is_unique: bool
    sample_values: List[Any] = []
    min_val: Optional[Any] = None
    max_val: Optional[Any] = None
    mean_val: Optional[float] = None

class DatasetProfile(BaseModel):
    dataset_name: str
    file_name: str
    row_count: int
    column_count: int
    data_quality_score: float # 0 to 100
    likely_primary_keys: List[str]
    columns: List[ColumnProfile]
    file_size_bytes: int

class DetectedRelationship(BaseModel):
    source_dataset: str
    source_column: str
    target_dataset: str
    target_column: str
    relationship_type: str # '1:N' or 'N:1' or '1:1'
    match_rate_pct: float
    confidence: str # 'High', 'Medium', 'Low'

class DatasetsOverview(BaseModel):
    datasets: List[DatasetProfile]
    relationships: List[DetectedRelationship]
    overall_quality_score: float

# 2. Analysis Plan Schemas
class AnalysisStep(BaseModel):
    step_number: int
    title: str
    method: str
    description: str
    target_metrics: List[str]
    status: str = "COMPLETED" # PENDING, RUNNING, COMPLETED

class AnalysisPlan(BaseModel):
    case_id: str
    case_title: str
    business_question: str
    steps: List[AnalysisStep]
    estimated_impact_area: str

# 3. KPI & Executive Overview Schemas
class KPISummary(BaseModel):
    revenue_prior: float
    revenue_current: float
    revenue_growth_pct: float
    
    gross_profit_prior: float
    gross_profit_current: float
    gross_profit_growth_pct: float
    
    net_profit_prior: float
    net_profit_current: float
    net_profit_growth_pct: float
    
    net_margin_prior_pct: float
    net_margin_current_pct: float
    net_margin_delta_pp: float # percentage points
    
    orders_prior: int
    orders_current: int
    orders_growth_pct: float
    
    aov_prior: float
    aov_current: float
    aov_growth_pct: float
    
    active_customers_prior: int
    active_customers_current: int
    active_customers_growth_pct: float
    
    cac_prior: float
    cac_current: float
    cac_growth_pct: float
    
    churn_rate_prior_pct: float
    churn_rate_current_pct: float
    churn_rate_delta_pp: float
    
    currency_symbol: str = "$"

# 4. Driver Tree Schemas
class DriverNode(BaseModel):
    id: str
    label: str
    metric_name: str
    prior_value: float
    current_value: float
    delta_value: float
    delta_pct: float
    contribution_pct: float # Contribution to parent change
    impact_magnitude: float
    currency: str = "$"
    trend: str # 'up', 'down', 'flat'
    status: str # 'positive', 'negative', 'neutral'
    affected_segments: List[str] = []
    children: List["DriverNode"] = []
    evidence_id: Optional[str] = None

# 5. Evidence & Classified Insights
class EvidenceDetail(BaseModel):
    evidence_id: str
    title: str
    methodology: str
    mathematical_formula: str
    sql_query: str
    sample_records: List[Dict[str, Any]]
    aggregate_table: List[Dict[str, Any]]

class ExecutiveInsight(BaseModel):
    id: str
    classification: StatementType # FACT, INSIGHT, HYPOTHESIS, RECOMMENDATION
    headline: str
    narrative: str
    magnitude_value: Optional[float] = None
    magnitude_formatted: Optional[str] = None
    affected_area: str
    confidence: str # High, Medium, Low
    evidence_id: str

# 6. Scenario Simulation Schemas
class ScenarioLevers(BaseModel):
    price_change_pct: float = 0.0        # e.g., +5%
    marketing_spend_delta_pct: float = 0.0 # e.g., -10%
    churn_rate_delta_pp: float = 0.0      # e.g., -2.0 pp
    delivery_cost_delta_pct: float = 0.0  # e.g., -8%
    cogs_reduction_pct: float = 0.0       # e.g., -3%
    return_rate_delta_pp: float = 0.0     # e.g., -1.5 pp

class MetricComparison(BaseModel):
    metric_name: str
    base_value: float
    scenario_value: float
    absolute_delta: float
    percentage_delta: float
    formatted_base: str
    formatted_scenario: str
    formatted_delta: str
    is_positive_trend: bool

class ScenarioResult(BaseModel):
    levers: ScenarioLevers
    metrics: Dict[str, MetricComparison]
    waterfall_breakdown: List[Dict[str, Any]]
    executive_verdict: str
    key_assumptions: List[str]

# 7. Strategic Recommendations
class StrategicRecommendation(BaseModel):
    id: str
    title: str
    recommendation: str
    why: str
    expected_impact_annualized: float
    expected_impact_formatted: str
    confidence: str # High, Medium, Low
    implementation_timeframe: str # Quick Win (0-30d), Tactical (1-3mo), Strategic (3-6mo)
    assumptions: List[str]
    supporting_evidence_ids: List[str]

# 8. Complete Consulting Engagement Package
class ConsultingDashboard(BaseModel):
    company_name: str = "NovaMart"
    industry: str = "E-commerce"
    quarter_evaluated: str = "Q3 2024 vs Q2 2024"
    problem_title: str = "Profitability Decline"
    kpi_summary: KPISummary
    driver_tree: DriverNode
    insights: List[ExecutiveInsight]
    recommendations: List[StrategicRecommendation]
    p_and_l_waterfall: List[Dict[str, Any]]
    monthly_trend: List[Dict[str, Any]]
    category_performance: List[Dict[str, Any]]
    marketing_efficiency: List[Dict[str, Any]]
    shipping_partner_breakdown: List[Dict[str, Any]]
