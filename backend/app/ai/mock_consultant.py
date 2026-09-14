from typing import Dict, Any, List
from app.ai.base import BaseAIProvider
from app.models.schemas import (
    AnalysisPlan, AnalysisStep, ExecutiveInsight, StatementType, KPISummary
)

class MockStrategicConsultant(BaseAIProvider):
    """
    Deterministic Strategic Consultant engine operating locally without external API dependencies.
    Provides authentic McKinsey/Bain/BCG structured decision frameworks.
    """

    def generate_analysis_plan(self, business_problem: str, dataset_overview: Dict[str, Any]) -> AnalysisPlan:
        # Check standard cases
        prob_lower = business_problem.lower()
        
        if "churn" in prob_lower or "retention" in prob_lower:
            return AnalysisPlan(
                case_id="case_churn",
                case_title="Customer Churn & Cohort Retention Diagnostic",
                business_question=business_problem,
                estimated_impact_area="Customer Lifetime Value & Recurring Revenue",
                steps=[
                    AnalysisStep(step_number=1, title="Cohort Retention Mapping", method="SQL / Cohort Analysis", description="Segment signups by quarter and calculate repeat purchase rates at 30, 60, and 90-day intervals.", target_metrics=["Cohort Retention %", "Repeat Order Rate"]),
                    AnalysisStep(step_number=2, title="Regional Churn Decomposition", method="Geographic Segmentation", description="Identify whether churn is localized to specific logistics zones or delivery tiers.", target_metrics=["Regional Churn Rate", "Order Defection %"]),
                    AnalysisStep(step_number=3, title="First-Order Experience Correlation", method="Bivariate Correlation", description="Analyze correlation between delivery delays/fees on first orders and churn propensity.", target_metrics=["On-time Delivery %", "Delivery Surcharge Impact"]),
                    AnalysisStep(step_number=4, title="Customer Lifetime Value Sizing", method="LTV Modeling", description="Quantify total revenue at risk from elevated churn rate vs historic benchmark.", target_metrics=["Annualized LTV Loss", "Payback Period Drift"])
                ]
            )
            
        # Default to Profitability Decline
        return AnalysisPlan(
            case_id="case_profit_decline",
            case_title="Profitability Decline & Driver Tree Diagnostic",
            business_question=business_problem,
            estimated_impact_area="Operating Margin & Net Profitability",
            steps=[
                AnalysisStep(step_number=1, title="Executive P&L Period-over-Period Variance", method="Waterfall Decomposition", description="Compare Net Revenue, COGS, Delivery Costs, and Marketing Spend QoQ.", target_metrics=["Net Revenue", "Gross Margin", "Operating Margin"]),
                AnalysisStep(step_number=2, title="Volume vs Price / AOV Decomposition", method="Factor Contribution Analysis", description="Isolate top-line decline between unit order volume and basket size/promotional discounts.", target_metrics=["Orders", "Average Order Value (AOV)", "Discount Rate"]),
                AnalysisStep(step_number=3, title="Logistics & Last-Mile Cost Audit", method="Vendor Contract Variance", description="Evaluate per-order fulfillment costs across shipping partners and identify rate inflation.", target_metrics=["Delivery Cost / Order", "Vendor Rate Delta"]),
                AnalysisStep(step_number=4, title="Marketing CAC & ROAS Efficiency Screening", method="Attribution Unit Economics", description="Analyze customer acquisition cost (CAC) and ROAS across Paid Social, Google Ads, and Affiliate.", target_metrics=["CAC", "ROAS", "Blended Payback"]),
                AnalysisStep(step_number=5, title="Category & SKU Margin Pareto Analysis", method="Pareto 80/20 & Margin Drift", description="Identify product categories experiencing margin compression and inventory discount fatigue.", target_metrics=["Category Gross Margin %", "Pareto Contribution"]),
                AnalysisStep(step_number=6, title="Synthesize Root Causes & Driver Tree", method="Hierarchical Driver Tree", description="Assemble verified mathematical findings into an executive decision tree.", target_metrics=["Contribution %", "Impact Magnitude ($)"])
            ]
        )

    def synthesize_executive_narrative(
        self, problem_title: str, kpi: KPISummary, root_cause_summary: str
    ) -> str:
        return (
            f"During the current quarter (Q3 2024), NovaMart experienced a {abs(kpi.net_profit_growth_pct):.1f}% contraction "
            f"in net operating profit, declining from ${kpi.net_profit_prior:,.0f} to ${kpi.net_profit_current:,.0f}. "
            f"The diagnostic reveals that 52% of this contraction stems from a 13.7% spike in fulfillment logistics costs "
            f"(predominantly FastLogistics rate hikes), exacerbated by a 5.1% erosion in Average Order Value (AOV) "
            f"and 38.2% CAC inflation in Paid Social channels. Corrective vendor re-allocation and minimum order thresholds "
            f"can restore an estimated $420,000 in annualized operating income."
        )

    def formulate_hypotheses(
        self, anomalies: List[Dict[str, Any]], context: Dict[str, Any]
    ) -> List[ExecutiveInsight]:
        return [
            ExecutiveInsight(
                id="ins_hypo_logistics_fuel",
                classification=StatementType.HYPOTHESIS,
                headline="Carrier fuel surcharge adjustments exceeded industry averages",
                narrative="FastLogistics instituted an unannounced surcharge increase in July 2024. Benchmarking suggests market rates increased by only 4.2% while NovaMart was billed +17.1%.",
                magnitude_value=105400.0,
                magnitude_formatted="$105.4K Variance",
                affected_area="Vendor Management",
                confidence="Medium",
                evidence_id="ev_shipping_surge"
            )
        ]
