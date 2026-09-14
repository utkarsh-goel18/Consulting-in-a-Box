from __future__ import annotations

import json
import os
from fastapi import APIRouter

from app.core.analysis_service import build_consulting_snapshot, invalidate
from app.core.config import settings
from app.core.database import repo
from app.engine.fast_demo_data import generate_fast_demo_datasets
from app.models.schemas import ConsultingDashboard

router = APIRouter(prefix="/demo", tags=["demo"])
_cached_dashboard: ConsultingDashboard | None = None

DASHBOARD_CACHE_VERSION = "pnl-v4-accounting-schema"


def _cache_path() -> str:
    return os.path.join(settings.DATA_DIR, f".novamart_dashboard_cache_{DASHBOARD_CACHE_VERSION}.json")


def clear_dashboard_cache() -> None:
    global _cached_dashboard
    _cached_dashboard = None
    try:
        os.remove(_cache_path())
    except OSError:
        pass


def _cache_is_valid(dashboard: ConsultingDashboard) -> bool:
    waterfall = dashboard.p_and_l_waterfall
    if not waterfall:
        return False
    totals = [row for row in waterfall if row.type == "total"]
    if len(totals) < 2:
        return False
    prior = float(totals[0].amount)
    current = float(totals[-1].amount)
    impacts = sum(float(row.amount) for row in waterfall if row.type != "total")
    return abs((prior + impacts) - current) <= 0.05


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

    # Uploads and the demo are deliberately separate workspaces. Previously, clicking
    # Run Demo after an upload caused the analytics engine to run against the uploaded
    # schema and could fail on fields that only exist in the NovaMart fixture.
    if not repo.is_demo_workspace:
        _restore_demo_workspace()

    if _cached_dashboard is not None:
        return _cached_dashboard

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
    if not _cache_is_valid(_cached_dashboard):
        raise RuntimeError("Deterministic P&L waterfall failed reconciliation.")
    try:
        with open(cache, "w", encoding="utf-8") as handle:
            json.dump(_cached_dashboard.model_dump(mode="json"), handle)
    except OSError:
        pass
    return _cached_dashboard
