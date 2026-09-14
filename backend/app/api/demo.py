from __future__ import annotations

import json
import math
import os
from fastapi import APIRouter

from app.core.analysis_service import build_consulting_snapshot, invalidate
from app.core.config import settings
from app.core.database import repo
from app.engine.fast_demo_data import generate_fast_demo_datasets
from app.models.schemas import ConsultingDashboard

router = APIRouter(prefix="/demo", tags=["demo"])
_cached_dashboard: ConsultingDashboard | None = None

DASHBOARD_CACHE_VERSION = "pnl-v6-robust-validation"


def _cache_path() -> str:
    return os.path.join(settings.DATA_DIR, f".novamart_dashboard_cache_{DASHBOARD_CACHE_VERSION}.json")


def clear_dashboard_cache() -> None:
    global _cached_dashboard
    _cached_dashboard = None
    try:
        os.remove(_cache_path())
    except OSError:
        pass


def _finite(value: object) -> bool:
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def _validation_error(dashboard: ConsultingDashboard) -> str | None:
    """Return a precise reason when a dashboard is not safe for the UI."""
    kpi = dashboard.kpi_summary
    required_kpis = (
        "revenue_prior", "revenue_current", "revenue_growth_pct",
        "gross_profit_prior", "gross_profit_current", "gross_profit_growth_pct",
        "net_profit_prior", "net_profit_current", "net_profit_growth_pct",
        "net_margin_prior_pct", "net_margin_current_pct", "net_margin_delta_pp",
        "orders_prior", "orders_current", "orders_growth_pct",
        "aov_prior", "aov_current", "aov_growth_pct",
        "active_customers_prior", "active_customers_current", "active_customers_growth_pct",
        "cac_prior", "cac_current", "cac_growth_pct",
        "churn_rate_prior_pct", "churn_rate_current_pct", "churn_rate_delta_pp",
    )
    bad = [field for field in required_kpis if not _finite(getattr(kpi, field, None))]
    if bad:
        return f"non-finite KPI fields: {', '.join(bad)}"

    waterfall = dashboard.p_and_l_waterfall
    if not waterfall:
        return "empty P&L waterfall"
    if not all(isinstance(row, dict) for row in waterfall):
        return "waterfall contains a non-dictionary row"
    if not all(isinstance(row.get("step"), str) for row in waterfall):
        return "waterfall contains a row without a step"
    if not all(_finite(row.get("amount")) and _finite(row.get("running_total")) for row in waterfall):
        return "waterfall contains a non-finite amount or running total"

    totals = [row for row in waterfall if row.get("type") == "total"]
    if len(totals) < 2:
        return "waterfall does not contain prior/current total rows"

    prior = float(totals[0]["amount"])
    current = float(totals[-1]["amount"])
    impacts = sum(float(row["amount"]) for row in waterfall if row.get("type") != "total")
    reconciliation_gap = abs((prior + impacts) - current)
    if reconciliation_gap > 1.0:
        return f"P&L reconciliation gap is {reconciliation_gap:.2f}"
    return None


def _cache_is_valid(dashboard: ConsultingDashboard) -> bool:
    return _validation_error(dashboard) is None


def _restore_demo_workspace() -> None:
    """Restore the canonical NovaMart fixture after a user has uploaded another workspace."""
    generate_fast_demo_datasets(settings.DATA_DIR)
    repo.dataframes.clear()
    for table in ("customers", "products", "orders", "order_items", "marketing_spend", "expenses", "returns"):
        path = os.path.join(settings.DATA_DIR, f"{table}.csv")
        if os.path.exists(path):
            import pandas as pd
            repo.register_dataframe(table, pd.read_csv(path))
    repo.workspace_name = "NovaMart"
    repo.is_demo_workspace = True
    invalidate()
    clear_dashboard_cache()


@router.post("/bootstrap", response_model=ConsultingDashboard)
def bootstrap_demo() -> ConsultingDashboard:
    """Return the canonical NovaMart demo snapshot, never an uploaded workspace."""
    global _cached_dashboard

    if not repo.is_demo_workspace:
        _restore_demo_workspace()

    if _cached_dashboard is not None:
        if _cache_is_valid(_cached_dashboard):
            return _cached_dashboard
        _cached_dashboard = None

    cache = _cache_path()
    if os.path.exists(cache):
        try:
            with open(cache, encoding="utf-8") as handle:
                candidate = ConsultingDashboard.model_validate(json.load(handle))
            if _cache_is_valid(candidate):
                _cached_dashboard = candidate
                return _cached_dashboard
            os.remove(cache)
        except Exception:
            try:
                os.remove(cache)
            except OSError:
                pass

    snapshot = build_consulting_snapshot()
    _cached_dashboard = ConsultingDashboard(
        company_name=snapshot["company_name"],
        industry=snapshot["industry"],
        quarter_evaluated=snapshot["quarter_evaluated"],
        problem_title=snapshot["problem_title"],
        kpi_summary=snapshot["kpi_summary"],
        driver_tree=snapshot["driver_tree"],
        insights=snapshot["insights"],
        recommendations=snapshot["recommendations"],
        p_and_l_waterfall=snapshot["waterfall"],
        monthly_trend=snapshot["monthly_trend"],
        category_performance=snapshot["category_performance"],
        marketing_efficiency=snapshot["marketing_efficiency"],
        shipping_partner_breakdown=snapshot["shipping_partner_breakdown"],
    )
    validation_error = _validation_error(_cached_dashboard)
    if validation_error:
        raise RuntimeError(f"Deterministic demo dashboard validation failed: {validation_error}")
    try:
        with open(cache, "w", encoding="utf-8") as handle:
            json.dump(_cached_dashboard.model_dump(mode="json"), handle)
    except OSError:
        pass
    return _cached_dashboard
