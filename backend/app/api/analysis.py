from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict, Any
from app.ai import get_ai_provider
from app.core.database import repo
from app.engine.analytics_engine import DeterministicAnalyticsEngine
from app.models.schemas import AnalysisPlan

router = APIRouter(prefix="/analysis", tags=["analysis"])

PREDEFINED_CASES = [
    {
        "id": "case_profitability_decline",
        "title": "Profitability Decline",
        "category": "Financial Performance",
        "default_question": "Our net operating profit declined significantly this quarter. Identify the root-cause drivers and margin compression factors.",
        "icon": "TrendingDown"
    },
    {
        "id": "case_customer_churn",
        "title": "Customer Churn",
        "category": "Customer & Retention",
        "default_question": "Customer defection and churn rates have escalated. Which customer cohorts and regional segments are churning, and what operational triggers correlate with abandonment?",
        "icon": "Users"
    },
    {
        "id": "case_revenue_growth",
        "title": "Revenue Growth",
        "category": "Top-Line Expansion",
        "default_question": "Identify high-elasticity product categories and pricing levers to accelerate top-line revenue without degrading gross margins.",
        "icon": "BarChart3"
    },
    {
        "id": "case_cost_optimization",
        "title": "Cost Optimization",
        "category": "Supply Chain & Operations",
        "default_question": "Audit operating expenditures across logistics carriers, warehousing facilities, and software vendors to uncover cost-reduction opportunities.",
        "icon": "DollarSign"
    },
    {
        "id": "case_marketing_roi",
        "title": "Marketing ROI",
        "category": "Growth Marketing",
        "default_question": "Attributed CAC has increased while blended ROAS is falling. Diagnose channel-level efficiency and recommend budget reallocation.",
        "icon": "Target"
    },
    {
        "id": "case_sales_performance",
        "title": "Sales Performance",
        "category": "Commercial Operations",
        "default_question": "Analyze average order values, discount distribution, and cart conversion across customer tiers to enhance sales productivity.",
        "icon": "ShoppingBag"
    },
    {
        "id": "case_inventory_optimization",
        "title": "Inventory Optimization",
        "category": "Merchandising",
        "default_question": "Detect slow-moving inventory, stockout risks, and return rate anomalies across high-volume product categories.",
        "icon": "Package"
    },
    {
        "id": "case_operational_efficiency",
        "title": "Operational Efficiency",
        "category": "Operations",
        "default_question": "Pinpoint bottlenecks in fulfillment dispatch, carrier SLA compliance, and reverse logistics return handling.",
        "icon": "Activity"
    }
]

class PlanRequest(BaseModel):
    case_id: str
    custom_problem: str = ""

@router.get("/cases")
def get_consulting_cases():
    """Returns the 8 predefined consulting engagement archetypes."""
    return PREDEFINED_CASES

@router.post("/plan", response_model=AnalysisPlan)
def generate_plan(req: PlanRequest):
    """Generates an executive analysis plan via AI abstraction layer."""
    selected_case = next((c for c in PREDEFINED_CASES if c["id"] == req.case_id), None)
    problem_text = req.custom_problem if req.custom_problem.strip() else (
        selected_case["default_question"] if selected_case else req.case_id
    )
    
    ai_provider = get_ai_provider()
    return ai_provider.generate_analysis_plan(problem_text, {k: len(v) for k, v in repo.dataframes.items()})
