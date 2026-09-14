from fastapi import APIRouter, Response
from app.core.database import repo
from app.engine.analytics_engine import DeterministicAnalyticsEngine
from app.engine.driver_tree import build_driver_tree
from app.engine.recommendation_engine import generate_classified_insights, generate_strategic_recommendations
from app.reports.pdf_generator import generate_consulting_pdf

router = APIRouter(prefix="/reports", tags=["reports"])


def get_report_payload():
    engine = DeterministicAnalyticsEngine(repo.dataframes)
    snapshot = engine.analysis_snapshot()
    costs = engine._period_costs()
    snapshot["costs"] = {"marketing_delta": costs["Marketing Spend"][1] - costs["Marketing Spend"][0]}
    snapshot["delivery_current"] = costs["Delivery Costs"][1]
    kpi = snapshot["kpi"]
    driver_tree = build_driver_tree(kpi, snapshot)
    insights = generate_classified_insights(kpi, snapshot)
    recs = generate_strategic_recommendations(kpi, snapshot)
    q_prior, q_curr = engine._quarters()
    return {
        "company_name": "NovaMart", "industry": "E-commerce", "quarter_evaluated": f"{q_curr} vs {q_prior}",
        "problem_title": "Profitability & Growth Performance", "currency": "INR", "currency_symbol": "₹",
        "kpi_summary": kpi.model_dump(), "driver_tree": driver_tree.model_dump(),
        "insights": [i.model_dump() for i in insights], "recommendations": [r.model_dump() for r in recs],
        "waterfall": snapshot["waterfall"], "category_performance": snapshot["categories"],
        "marketing_efficiency": snapshot["marketing"], "shipping_partner_breakdown": snapshot["shipping"],
    }


@router.get("/content")
def get_consulting_report_data():
    return get_report_payload()


@router.get("/download-pdf")
def download_pdf_report():
    payload = get_report_payload()
    pdf_bytes = generate_consulting_pdf(payload)
    return Response(content=pdf_bytes, media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=Consulting_Report_NovaMart_INR.pdf"})
