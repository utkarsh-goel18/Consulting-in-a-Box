from fastapi import APIRouter, Response
from app.core.database import repo
from app.engine.analytics_engine import DeterministicAnalyticsEngine
from app.engine.driver_tree import build_driver_tree
from app.engine.recommendation_engine import (
    generate_classified_insights, generate_strategic_recommendations
)
from app.reports.pdf_generator import generate_consulting_pdf

router = APIRouter(prefix="/reports", tags=["reports"])

def get_report_payload():
    engine = DeterministicAnalyticsEngine(repo.dataframes)
    kpi = engine.calculate_executive_kpis()
    driver_tree = build_driver_tree(kpi)
    insights = generate_classified_insights(kpi)
    recs = generate_strategic_recommendations(kpi)
    
    return {
        "company_name": "NovaMart",
        "industry": "E-commerce",
        "quarter_evaluated": "Q3 2024 vs Q2 2024",
        "problem_title": "Profitability Decline & Margin Diagnostic",
        "kpi_summary": kpi.model_dump(),
        "driver_tree": driver_tree.model_dump(),
        "insights": [i.model_dump() for i in insights],
        "recommendations": [r.model_dump() for r in recs]
    }

@router.get("/content")
def get_consulting_report_data():
    """Returns the complete 10-section consulting report structure."""
    return get_report_payload()

@router.get("/download-pdf")
def download_pdf_report():
    """Generates and streams the executive consulting deliverable in PDF format."""
    payload = get_report_payload()
    pdf_bytes = generate_consulting_pdf(payload)
    
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": "attachment; filename=Consulting_Report_NovaMart_Executive_Diagnostic.pdf"
        }
    )
