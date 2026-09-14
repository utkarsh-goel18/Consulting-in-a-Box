from fastapi import APIRouter, Response

from app.core.analysis_service import build_consulting_snapshot
from app.reports.pdf_generator import generate_consulting_pdf

router = APIRouter(prefix="/reports", tags=["reports"])


def get_report_payload():
    snapshot = build_consulting_snapshot()
    return {
        "company_name": snapshot["company_name"],
        "industry": snapshot["industry"],
        "quarter_evaluated": snapshot["quarter_evaluated"],
        "problem_title": snapshot["problem_title"],
        "currency": "INR",
        "currency_symbol": "₹",
        "kpi_summary": snapshot["kpi_summary"].model_dump(),
        "driver_tree": snapshot["driver_tree"].model_dump(),
        "insights": [item.model_dump() for item in snapshot["insights"]],
        "recommendations": [item.model_dump() for item in snapshot["recommendations"]],
        "waterfall": snapshot["waterfall"],
        "monthly_trend": snapshot["monthly_trend"],
        "category_performance": snapshot["category_performance"],
        "marketing_efficiency": snapshot["marketing_efficiency"],
        "shipping_partner_breakdown": snapshot["shipping_partner_breakdown"],
        "costs": snapshot["costs"],
    }


@router.get("/content")
def get_consulting_report_data():
    return get_report_payload()


@router.get("/download-pdf")
def download_pdf_report():
    payload = get_report_payload()
    pdf_bytes = generate_consulting_pdf(payload)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=Consulting_Report_NovaMart_INR.pdf"},
    )
