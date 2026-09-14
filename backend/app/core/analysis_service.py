from __future__ import annotations

from typing import Any, Dict

from app.core.database import repo
from app.engine.analytics_engine import DeterministicAnalyticsEngine
from app.engine.driver_tree import build_driver_tree
from app.engine.recommendation_engine import generate_classified_insights, generate_strategic_recommendations

_engine: DeterministicAnalyticsEngine | None = None
_signature: tuple[tuple[str, int, int], ...] | None = None


def _data_signature() -> tuple[tuple[str, int, int], ...]:
    return tuple(sorted((name, id(df), len(df)) for name, df in repo.dataframes.items()))


def get_engine() -> DeterministicAnalyticsEngine:
    global _engine, _signature
    signature = _data_signature()
    if _engine is None or _signature != signature:
        _engine = DeterministicAnalyticsEngine(repo.dataframes)
        _signature = signature
    return _engine


def invalidate() -> None:
    global _engine, _signature
    _engine = None
    _signature = None


def get_snapshot() -> Dict[str, Any]:
    engine = get_engine()
    snapshot = engine.analysis_snapshot()
    costs = engine._period_costs()
    snapshot["costs"] = {name: {"prior": values[0], "current": values[1], "delta": values[1] - values[0]} for name, values in costs.items()}
    snapshot["delivery_current"] = costs["Delivery Costs"][1]
    return snapshot


def build_consulting_snapshot() -> Dict[str, Any]:
    snapshot = get_snapshot()
    kpi = snapshot["kpi"]
    driver_tree = build_driver_tree(kpi, snapshot)
    insights = generate_classified_insights(kpi, snapshot)
    recommendations = generate_strategic_recommendations(kpi, snapshot)
    engine = get_engine()
    q_prior, q_curr = engine._quarters()
    return {
        "company_name": repo.workspace_name,
        "industry": "E-commerce / Business Dataset",
        "quarter_evaluated": f"{q_curr} vs {q_prior}",
        "problem_title": "Profitability Decline",
        "kpi_summary": kpi,
        "driver_tree": driver_tree,
        "insights": insights,
        "recommendations": recommendations,
        "waterfall": snapshot["waterfall"],
        "monthly_trend": snapshot.get("monthly_trend", []),
        "category_performance": snapshot["categories"],
        "marketing_efficiency": snapshot["marketing"],
        "shipping_partner_breakdown": snapshot["shipping"],
        "costs": snapshot["costs"],
    }
