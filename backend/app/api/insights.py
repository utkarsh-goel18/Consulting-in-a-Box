from fastapi import APIRouter, HTTPException
from typing import List
from app.core.database import repo
from app.engine.analytics_engine import DeterministicAnalyticsEngine
from app.engine.driver_tree import build_driver_tree
from app.engine.recommendation_engine import generate_classified_insights, get_evidence_catalog
from app.models.schemas import DriverNode, ExecutiveInsight, EvidenceDetail

router = APIRouter(prefix="/insights", tags=["insights"])


def _snapshot():
    engine = DeterministicAnalyticsEngine(repo.dataframes)
    snapshot = engine.analysis_snapshot()
    costs = engine._period_costs()
    snapshot["costs"] = {"marketing_delta": costs["Marketing Spend"][1] - costs["Marketing Spend"][0]}
    snapshot["delivery_current"] = costs["Delivery Costs"][1]
    return snapshot


@router.get("/tree", response_model=DriverNode)
def get_driver_tree():
    snapshot = _snapshot()
    return build_driver_tree(snapshot["kpi"], snapshot)


@router.get("/classified", response_model=List[ExecutiveInsight])
def get_classified_insights():
    snapshot = _snapshot()
    return generate_classified_insights(snapshot["kpi"], snapshot)


@router.get("/evidence/{evidence_id}", response_model=EvidenceDetail)
def get_evidence_detail(evidence_id: str):
    snapshot = _snapshot()
    catalog = get_evidence_catalog(snapshot["kpi"], snapshot)
    if evidence_id not in catalog:
        raise HTTPException(status_code=404, detail=f"Evidence ID {evidence_id} not found in catalog.")
    return catalog[evidence_id]
