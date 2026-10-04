from typing import Any, Dict

from fastapi import APIRouter, Response

from app.core.analysis_service import build_consulting_snapshot
from app.reports.pdf_generator import generate_consulting_pdf
from app.core.currency import json_safe

router = APIRouter(prefix="/reports", tags=["reports"])


def _snapshot_to_payload(snapshot: Dict[str, Any]) -> Dict[str, Any]:
    raw = {
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
    return json_safe(raw)


def get_report_payload():
    return _snapshot_to_payload(build_consulting_snapshot())


def _dashboard_to_payload(dashboard: Dict[str, Any]) -> Dict[str, Any]:
    # Accept the exact dashboard snapshot already rendered in the browser.
    # This prevents the PDF from silently switching back to a server-side
    # cached/default demo workspace when the user has analyzed uploaded data.
    raw = {
        "company_name": dashboard.get("company_name", "Uploaded Workspace"),
        "industry": dashboard.get("industry", "E-commerce / Business Dataset"),
        "quarter_evaluated": dashboard.get("quarter_evaluated", ""),
        "problem_title": dashboard.get("problem_title", "Business Performance"),
        "currency": "INR",
        "currency_symbol": "₹",
        "kpi_summary": dashboard.get("kpi_summary", {}),
        "driver_tree": dashboard.get("driver_tree", {}),
        "insights": dashboard.get("insights", []),
        "recommendations": dashboard.get("recommendations", []),
        "waterfall": dashboard.get("p_and_l_waterfall", dashboard.get("waterfall", [])),
        "monthly_trend": dashboard.get("monthly_trend", []),
        "category_performance": dashboard.get("category_performance", []),
        "marketing_efficiency": dashboard.get("marketing_efficiency", []),
        "shipping_partner_breakdown": dashboard.get("shipping_partner_breakdown", []),
        "costs": dashboard.get("costs", {}),
    }
    return json_safe(raw)


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


@router.post("/download-pdf")
def download_dashboard_pdf(dashboard: Dict[str, Any]):
    payload = _dashboard_to_payload(dashboard)
    pdf_bytes = generate_consulting_pdf(payload)
    company_name = str(payload.get("company_name") or "Uploaded_Workspace").replace(" ", "_")
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=Consulting_Report_{company_name}_INR.pdf"},
    )
