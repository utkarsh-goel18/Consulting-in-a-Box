from typing import Dict, Any, List
from app.ai.base import BaseAIProvider
from app.models.schemas import AnalysisPlan, AnalysisStep, ExecutiveInsight, StatementType, KPISummary
from app.core.currency import format_inr


CASE_PLANS = {
    "case_profitability_decline": ("Profitability Decline", "Financial Performance", [
        ("P&L variance", "Waterfall decomposition", "Reconcile revenue, COGS, delivery, marketing, opex and returns period over period.", ["Revenue", "Gross Profit", "Net Profit"]),
        ("Volume vs AOV", "Factor contribution", "Separate order-volume and basket-size effects on revenue.", ["Orders", "AOV"]),
        ("Cost driver audit", "Variance analysis", "Identify the cost categories responsible for profit pressure.", ["COGS", "Delivery Cost", "Marketing Spend"]),
        ("Root-cause synthesis", "Driver tree", "Rank verified drivers by contribution and evidence strength.", ["Contribution %", "Impact"]),
    ]),
    "case_customer_churn": ("Customer Churn", "Customer & Retention", [
        ("Cohort retention", "Cohort analysis", "Compare customer retention and churn signals across periods and segments.", ["Churn Rate", "Active Customers"]),
        ("Regional segmentation", "Geographic analysis", "Screen regions and tiers for abnormal customer defection.", ["Regional Churn", "Orders"]),
        ("Experience drivers", "Correlation screening", "Test operational signals against churn without asserting causality.", ["Delivery Cost", "Return Rate"]),
        ("Value at risk", "LTV sizing", "Estimate directional revenue/LTV exposure from observed churn changes.", ["LTV", "Revenue at Risk"]),
    ]),
    "case_revenue_growth": ("Revenue Growth", "Top-Line Expansion", [
        ("Revenue decomposition", "Orders × AOV", "Quantify volume and basket-size headroom.", ["Revenue", "Orders", "AOV"]),
        ("Category Pareto", "Contribution analysis", "Identify categories that drive the majority of revenue.", ["Category Revenue", "Pareto %"]),
        ("Pricing screen", "Elasticity sensitivity", "Model directional price and volume trade-offs.", ["Price", "Orders"]),
        ("Growth actions", "Scenario analysis", "Translate verified gaps into testable commercial actions.", ["Incremental Revenue", "Margin"]),
    ]),
    "case_cost_optimization": ("Cost Optimization", "Supply Chain & Operations", [
        ("Cost baseline", "Cost bridge", "Reconcile COGS, delivery, marketing, opex and returns.", ["Total Costs", "Net Profit"]),
        ("Carrier variance", "Vendor analysis", "Compare carrier rates and current-period volume.", ["Delivery Cost", "Excess Cost"]),
        ("Category margin", "Margin analysis", "Locate categories where cost inflation or pricing pressure matters most.", ["Gross Margin", "Margin %"]),
        ("Savings sizing", "Opportunity sizing", "Size recoverable cost pools and validate operational constraints.", ["Savings", "Payback"]),
    ]),
    "case_marketing_roi": ("Marketing ROI", "Growth Marketing", [
        ("Channel baseline", "Unit economics", "Calculate spend, attributed orders, CAC and ROAS by channel.", ["CAC", "ROAS"]),
        ("Efficiency drift", "Period variance", "Identify channels with material efficiency deterioration.", ["CAC Growth", "ROAS Change"]),
        ("Budget mix", "Portfolio analysis", "Compare incremental efficiency before recommending reallocation.", ["Spend", "ROAS"]),
        ("Reallocation scenario", "Sensitivity analysis", "Model directional profit impact of budget shifts.", ["Profit", "CAC"]),
    ]),
    "case_sales_performance": ("Sales Performance", "Commercial Operations", [
        ("Basket diagnostic", "AOV analysis", "Decompose changes in basket size and discounting.", ["AOV", "Discount"]),
        ("Customer segment mix", "Segmentation", "Compare purchasing patterns across customer segments.", ["Orders", "AOV"]),
        ("Category performance", "Margin analysis", "Identify categories with growth and margin headroom.", ["Revenue", "Margin"]),
        ("Commercial actions", "Scenario modeling", "Test targeted basket-building and pricing interventions.", ["Revenue", "Profit"]),
    ]),
    "case_inventory_optimization": ("Inventory Optimization", "Merchandising", [
        ("SKU velocity", "ABC/Pareto analysis", "Rank product demand and revenue concentration.", ["Revenue", "Volume"]),
        ("Margin exposure", "Contribution analysis", "Locate low-margin high-volume categories.", ["Margin", "COGS"]),
        ("Return signals", "Return-rate analysis", "Screen return reasons and category-level return exposure.", ["Return Rate", "Refunds"]),
        ("Action sizing", "Scenario analysis", "Model pricing, assortment and procurement interventions.", ["Profit", "Working Capital"]),
    ]),
    "case_operational_efficiency": ("Operational Efficiency", "Operations", [
        ("Fulfillment baseline", "Process KPI analysis", "Establish cost and volume baselines across operations.", ["Delivery Cost", "Orders"]),
        ("Carrier performance", "Vendor variance", "Identify rate and mix anomalies by shipping partner.", ["Carrier Cost", "Variance"]),
        ("Reverse logistics", "Return analysis", "Quantify refund and reverse-logistics pressure.", ["Returns", "Refunds"]),
        ("Operating actions", "Opportunity sizing", "Prioritize actions by impact, confidence and effort.", ["Savings", "Payback"]),
    ]),
}


class MockStrategicConsultant(BaseAIProvider):
    """Offline deterministic consultant. It structures questions; it never computes facts."""

    def generate_analysis_plan(self, business_problem: str, dataset_overview: Dict[str, Any]) -> AnalysisPlan:
        case_id = dataset_overview.get("case_id") or "case_profitability_decline"
        title, impact, raw_steps = CASE_PLANS.get(case_id, CASE_PLANS["case_profitability_decline"])
        steps = [AnalysisStep(step_number=i + 1, title=title, method=method, description=description, target_metrics=metrics) for i, (title, method, description, metrics) in enumerate(raw_steps)]
        return AnalysisPlan(case_id=case_id, case_title=title, business_question=business_problem, steps=steps, estimated_impact_area=impact)

    def synthesize_executive_narrative(self, problem_title: str, kpi: KPISummary, root_cause_summary: str) -> str:
        return f"{problem_title}: net profit moved from {format_inr(kpi.net_profit_prior)} to {format_inr(kpi.net_profit_current)} ({kpi.net_profit_growth_pct:+.1f}%). Revenue changed {kpi.revenue_growth_pct:+.1f}% and AOV changed {kpi.aov_growth_pct:+.1f}%. The analytical driver tree identifies the largest verified sources of variance; causal explanations remain hypotheses until validated."

    def formulate_hypotheses(self, anomalies: List[Dict[str, Any]], context: Dict[str, Any]) -> List[ExecutiveInsight]:
        return [ExecutiveInsight(id="ai_hypothesis_01", classification=StatementType.HYPOTHESIS, headline="An operational driver may explain the observed variance", narrative="This is a hypothesis generated from an anomaly signal. Validate it against operational records before treating it as causal.", magnitude_value=None, magnitude_formatted=None, affected_area="Operations", confidence="Medium", evidence_id="ev_cost_inflation")]
