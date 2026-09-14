from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from app.core.database import repo
from app.engine.analytics_engine import DeterministicAnalyticsEngine
from app.engine.driver_tree import build_driver_tree
from app.engine.recommendation_engine import (
    generate_classified_insights, get_evidence_catalog
)
from app.models.schemas import DriverNode, ExecutiveInsight, EvidenceDetail

router = APIRouter(prefix="/insights", tags=["insights"])

@router.get("/tree", response_model=DriverNode)
def get_driver_tree():
    """Returns the multi-tier hierarchical Driver Tree decomposing Net Profit variance."""
    engine = DeterministicAnalyticsEngine(repo.dataframes)
    kpi = engine.calculate_executive_kpis()
    return build_driver_tree(kpi)

@router.get("/classified", response_model=List[ExecutiveInsight])
def get_classified_insights():
    """Returns strictly classified findings (FACT, INSIGHT, HYPOTHESIS, RECOMMENDATION)."""
    engine = DeterministicAnalyticsEngine(repo.dataframes)
    kpi = engine.calculate_executive_kpis()
    return generate_classified_insights(kpi)

@router.get("/evidence/{evidence_id}", response_model=EvidenceDetail)
def get_evidence_detail(evidence_id: str):
    """Returns mathematical formulas, SQL queries, and underlying records supporting an insight."""
    catalog = get_evidence_catalog()
    if evidence_id not in catalog:
        raise HTTPException(status_code=404, detail=f"Evidence ID {evidence_id} not found in catalog.")
    return catalog[evidence_id]
