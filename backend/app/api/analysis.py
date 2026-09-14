from __future__ import annotations

import math
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from app.ai import get_ai_provider
from app.core.analysis_service import build_consulting_snapshot
from app.core.database import repo
from app.models.schemas import AnalysisPlan, ConsultingDashboard

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


def _json_safe(value: Any) -> Any:
    """Recursively remove NaN/Infinity from analytics payloads before JSON serialization.

    Analytics may legitimately produce an undefined percentage when its denominator is
    zero (for example CAC/ROAS for a channel with no attributable orders). The API must
    never emit non-standard JSON. Numeric non-finite values are represented as 0.0 at
    the transport boundary; the deterministic engine remains the source of truth.
    """
    if isinstance(value, float):
        return value if math.isfinite(value) else 0.0
    if isinstance(value, int) or value is None or isinstance(value, (str, bool)):
        return value
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_json_safe(item) for item in value]
    try:
        if hasattr(value, "item"):
            return _json_safe(value.item())
    except Exception:
        pass
    return value


@router.get("/cases")
def get_consulting_cases():
    return PREDEFINED_CASES


@router.post("/plan", response_model=AnalysisPlan)
def generate_plan(req: PlanRequest):
    selected = next((case for case in PREDEFINED_CASES if case["id"] == req.case_id), None)
    problem_text = req.custom_problem.strip() or (selected["default_question"] if selected else req.case_id)
    provider = get_ai_provider()
    return provider.generate_analysis_plan(problem_text, {"case_id": req.case_id, "workspace": repo.workspace_name, "tables": {k: len(v) for k, v in repo.dataframes.items()}})


@router.post("/execute")
def execute_analysis(req: PlanRequest):
    """Execute against the currently active workspace and return a complete dashboard."""
    plan = generate_plan(req)
    snapshot = build_consulting_snapshot()
    kpi = snapshot["kpi_summary"]
    dashboard = ConsultingDashboard(
        company_name=snapshot["company_name"],
        industry=snapshot["industry"],
        quarter_evaluated=snapshot["quarter_evaluated"],
        problem_title=snapshot["problem_title"],
        kpi_summary=kpi,
        driver_tree=snapshot["driver_tree"],
        insights=snapshot["insights"],
        recommendations=snapshot["recommendations"],
        p_and_l_waterfall=snapshot["waterfall"],
        monthly_trend=snapshot["monthly_trend"],
        category_performance=snapshot["category_performance"],
        marketing_efficiency=snapshot["marketing_efficiency"],
        shipping_partner_breakdown=snapshot["shipping_partner_breakdown"],
    )
    payload = {
        "case_id": req.case_id,
        "case_title": plan.case_title,
        "business_question": plan.business_question,
        "plan": plan.model_dump(),
        "timeline": [
            {"step": 1, "title": "Profile & validate inputs", "status": "COMPLETED", "detail": f"Validated {len(repo.dataframes)} datasets and their analytical relationships."},
            {"step": 2, "title": "Compute deterministic KPIs", "status": "COMPLETED", "detail": "Evaluated revenue, profit, orders, AOV, CAC and churn for the two latest quarters."},
            {"step": 3, "title": "Decompose root causes", "status": "COMPLETED", "detail": f"Built a reconciled P&L driver tree for {kpi.net_profit_growth_pct:+.1f}% net-profit movement."},
            {"step": 4, "title": "Classify findings", "status": "COMPLETED", "detail": f"Produced {len(snapshot['insights'])} FACT / INSIGHT / HYPOTHESIS statements with evidence IDs."},
            {"step": 5, "title": "Size actions & scenarios", "status": "COMPLETED", "detail": f"Generated {len(snapshot['recommendations'])} evidence-backed recommendations and deterministic what-if inputs."},
        ],
        "result": {
            "kpi_summary": kpi.model_dump(),
            "driver_tree": snapshot["driver_tree"].model_dump(),
            "insights": [item.model_dump() for item in snapshot["insights"]],
            "recommendations": [item.model_dump() for item in snapshot["recommendations"]],
        },
        "dashboard": dashboard.model_dump(mode="json"),
    }
    return _json_safe(payload)
