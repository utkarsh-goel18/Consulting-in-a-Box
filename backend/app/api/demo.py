from __future__ import annotations

import json
import os
from fastapi import APIRouter

from app.core.analysis_service import build_consulting_snapshot
from app.core.config import settings
from app.models.schemas import ConsultingDashboard

router = APIRouter(prefix="/demo", tags=["demo"])
_cached_dashboard: ConsultingDashboard | None = None


def _cache_path() -> str:
    return os.path.join(settings.DATA_DIR, ".novamart_dashboard_cache.json")


@router.post("/bootstrap", response_model=ConsultingDashboard)
def bootstrap_demo() -> ConsultingDashboard:
    """Return the deterministic NovaMart snapshot, using a disk + process cache."""
    global _cached_dashboard
    if _cached_dashboard is not None:
        return _cached_dashboard

    cache = _cache_path()
    if os.path.exists(cache):
        try:
            with open(cache, encoding="utf-8") as handle:
                _cached_dashboard = ConsultingDashboard.model_validate(json.load(handle))
                return _cached_dashboard
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
    try:
        with open(cache, "w", encoding="utf-8") as handle:
            json.dump(_cached_dashboard.model_dump(mode="json"), handle)
    except OSError:
        pass
    return _cached_dashboard
