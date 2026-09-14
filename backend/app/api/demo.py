from __future__ import annotations

import json
import os
from fastapi import APIRouter

from app.core.analysis_service import build_consulting_snapshot
from app.core.config import settings
from app.models.schemas import ConsultingDashboard

router = APIRouter(prefix="/demo", tags=["demo"])
_cached_dashboard: ConsultingDashboard | None = None

# Version the serialized dashboard separately from the analytical engine. This
# prevents a locally persisted snapshot created by an older waterfall formula
# from surviving a backend restart.
DASHBOARD_CACHE_VERSION = "pnl-v3-accounting-bridge"


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
    """Guard the most important contract of a P&L bridge before caching it."""
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


@router.post("/bootstrap", response_model=ConsultingDashboard)
def bootstrap_demo() -> ConsultingDashboard:
    """Return the deterministic NovaMart snapshot, using a versioned disk + process cache."""
    global _cached_dashboard
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
