from fastapi import APIRouter, HTTPException
from typing import List

from app.core.analysis_service import get_snapshot
from app.engine.driver_tree import build_driver_tree
from app.engine.recommendation_engine import generate_classified_insights, get_evidence_catalog
from app.models.schemas import DriverNode, ExecutiveInsight, EvidenceDetail

router = APIRouter(prefix="/insights", tags=["insights"])


@router.get("/tree", response_model=DriverNode)
def get_driver_tree():
    snapshot = get_snapshot()
    return build_driver_tree(snapshot["kpi"], snapshot)


@router.get("/classified", response_model=List[ExecutiveInsight])
def get_classified_insights():
    snapshot = get_snapshot()
    return generate_classified_insights(snapshot["kpi"], snapshot)


@router.get("/evidence/{evidence_id}", response_model=EvidenceDetail)
def get_evidence_detail(evidence_id: str):
    snapshot = get_snapshot()
    catalog = get_evidence_catalog(snapshot["kpi"], snapshot)
    if evidence_id not in catalog:
        raise HTTPException(status_code=404, detail=f"Evidence ID {evidence_id} not found in catalog.")
    return catalog[evidence_id]
