from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
from app.ai import get_ai_provider
from app.core.database import repo
from app.models.schemas import AnalysisPlan

router = APIRouter(prefix="/analysis", tags=["analysis"])

PREDEFINED_CASES = [
    {"id": "case_profitability_decline", "title": "Profitability Decline", "category": "Financial Performance", "default_question": "Our net operating profit declined. Identify the root-cause drivers and margin compression factors.", "icon": "TrendingDown"},
    {"id": "case_customer_churn", "title": "Customer Churn", "category": "Customer & Retention", "default_question": "Which customer cohorts and segments show the strongest churn signals, and which operational variables should be validated?", "icon": "Users"},
    {"id": "case_revenue_growth", "title": "Revenue Growth", "category": "Top-Line Expansion", "default_question": "Identify volume, basket and category levers that could accelerate revenue without degrading contribution margin.", "icon": "BarChart3"},
    {"id": "case_cost_optimization", "title": "Cost Optimization", "category": "Supply Chain & Operations", "default_question": "Audit logistics, operating expense and product cost drivers to uncover evidence-backed savings opportunities.", "icon": "DollarSign"},
    {"id": "case_marketing_roi", "title": "Marketing ROI", "category": "Growth Marketing", "default_question": "Diagnose channel-level CAC and ROAS changes and identify where budget reallocation should be tested.", "icon": "Target"},
    {"id": "case_sales_performance", "title": "Sales Performance", "category": "Commercial Operations", "default_question": "Analyze AOV, discounting, customer mix and category performance to improve commercial productivity.", "icon": "ShoppingBag"},
    {"id": "case_inventory_optimization", "title": "Inventory Optimization", "category": "Merchandising", "default_question": "Detect product/category concentration, margin exposure and return signals that should inform assortment decisions.", "icon": "Package"},
    {"id": "case_operational_efficiency", "title": "Operational Efficiency", "category": "Operations", "default_question": "Pinpoint fulfillment, carrier and reverse-logistics cost bottlenecks and prioritize operational actions.", "icon": "Activity"},
]


class PlanRequest(BaseModel):
    case_id: str
    custom_problem: str = ""


@router.get("/cases")
def get_consulting_cases():
    return PREDEFINED_CASES


@router.post("/plan", response_model=AnalysisPlan)
def generate_plan(req: PlanRequest):
    selected = next((c for c in PREDEFINED_CASES if c["id"] == req.case_id), None)
    problem_text = req.custom_problem.strip() or (selected["default_question"] if selected else req.case_id)
    provider = get_ai_provider()
    return provider.generate_analysis_plan(problem_text, {"case_id": req.case_id, "tables": {k: len(v) for k, v in repo.dataframes.items()}})
