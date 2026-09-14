import io
from typing import Dict, Any
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from app.core.currency import format_inr


def generate_consulting_pdf(dashboard_data: Dict[str, Any], output_path: str = None) -> bytes:
    """Generate the same data-driven ten-section executive report shown in the app."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(output_path or buffer, pagesize=A4, rightMargin=16*mm, leftMargin=16*mm, topMargin=16*mm, bottomMargin=16*mm)
    styles = getSampleStyleSheet()
    title = ParagraphStyle("Title", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=22, leading=27, textColor=colors.HexColor("#0f172a"), spaceAfter=8)
    h1 = ParagraphStyle("H1", parent=styles["Heading1"], fontName="Helvetica-Bold", fontSize=14, leading=18, textColor=colors.HexColor("#1e293b"), spaceBefore=10, spaceAfter=7)
    body = ParagraphStyle("Body", parent=styles["BodyText"], fontName="Helvetica", fontSize=8.8, leading=13, textColor=colors.HexColor("#334155"), spaceAfter=5)
    small = ParagraphStyle("Small", parent=body, fontSize=7.5, leading=10)
    callout = ParagraphStyle("Callout", parent=body, fontName="Helvetica-Bold", backColor=colors.HexColor("#eff6ff"), borderPadding=7, spaceAfter=8)
    story = []
    k = dashboard_data.get("kpi_summary", {})
    company = dashboard_data.get("company_name", "NovaMart")
    period = dashboard_data.get("quarter_evaluated", "Current vs Prior")
    symbol = dashboard_data.get("currency_symbol", "₹")

    story += [Paragraph("CONSULTING IN A BOX", ParagraphStyle("eyebrow", parent=small, fontName="Helvetica-Bold", textColor=colors.HexColor("#2563eb")), Paragraph("Executive Diagnostic & Decision Intelligence Report", title), Paragraph(f"{company} · {period} · INR", body), HRFlowable(width="100%", thickness=1, color=colors.HexColor("#0f172a")), Spacer(1, 7*mm)]

    # 1 Executive summary
    story.append(Paragraph("1. Executive Summary", h1))
    story.append(Paragraph(f"Net operating profit moved from {format_inr(k.get('net_profit_prior', 0))} to {format_inr(k.get('net_profit_current', 0))} ({k.get('net_profit_growth_pct', 0):+.1f}%) while revenue changed {k.get('revenue_growth_pct', 0):+.1f}%. The driver tree, P&L bridge and evidence vault below are generated from the same deterministic analytical snapshot.", callout))

    # 2 Problem definition
    story.append(Paragraph("2. Business Problem Definition", h1))
    story.append(Paragraph(f"<b>Problem:</b> {dashboard_data.get('problem_title', 'Business performance diagnostic')}<br/><b>Objective:</b> isolate material revenue and cost drivers, distinguish facts from hypotheses, and translate verified variance into testable actions.", body))

    # 3 KPI scorecard
    story.append(Paragraph("3. Strategic KPI Scorecard", h1))
    rows = [["Metric", "Prior", "Current", "Change"]]
    for label, p, c, change in [
        ("Revenue", k.get("revenue_prior", 0), k.get("revenue_current", 0), k.get("revenue_growth_pct", 0)),
        ("Gross Profit", k.get("gross_profit_prior", 0), k.get("gross_profit_current", 0), k.get("gross_profit_growth_pct", 0)),
        ("Net Profit", k.get("net_profit_prior", 0), k.get("net_profit_current", 0), k.get("net_profit_growth_pct", 0)),
        ("AOV", k.get("aov_prior", 0), k.get("aov_current", 0), k.get("aov_growth_pct", 0)),
        ("CAC", k.get("cac_prior", 0), k.get("cac_current", 0), k.get("cac_growth_pct", 0)),
    ]:
        rows.append([label, format_inr(p), format_inr(c), f"{change:+.1f}%"])
    rows += [["Orders", f"{k.get('orders_prior',0):,}", f"{k.get('orders_current',0):,}", f"{k.get('orders_growth_pct',0):+.1f}%"], ["Net Margin", f"{k.get('net_margin_prior_pct',0):.1f}%", f"{k.get('net_margin_current_pct',0):.1f}%", f"{k.get('net_margin_delta_pp',0):+.1f} pp"], ["Churn", f"{k.get('churn_rate_prior_pct',0):.1f}%", f"{k.get('churn_rate_current_pct',0):.1f}%", f"{k.get('churn_rate_delta_pp',0):+.1f} pp"]]
    table = Table(rows, colWidths=[50*mm, 38*mm, 38*mm, 30*mm])
    table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#0f172a')),('TEXTCOLOR',(0,0),(-1,0),colors.white),('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),('GRID',(0,0),(-1,-1),0.35,colors.HexColor('#cbd5e1')),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#f8fafc')]),('FONTSIZE',(0,0),(-1,-1),8)]))
    story += [table, Spacer(1, 5*mm)]

    # 4 Findings
    story.append(Paragraph("4. Major Findings & Classification", h1))
    for insight in dashboard_data.get("insights", []):
        story.append(Paragraph(f"<b>[{insight.get('classification')}] {insight.get('headline')}</b> — {insight.get('narrative')}", body))

    # 5 Driver tree
    story.append(Paragraph("5. Root Cause Driver Tree", h1))
    root = dashboard_data.get("driver_tree", {})
    story.append(Paragraph(f"<b>{root.get('label','Net Profit')}</b>: {format_inr(root.get('prior_value',0))} → {format_inr(root.get('current_value',0))} ({root.get('delta_pct',0):+.1f}%). The child drivers are calculated from the same P&L bridge and ranked by observed impact.", body))
    for child in root.get("children", []):
        story.append(Paragraph(f"• <b>{child.get('label')}</b>: {child.get('delta_pct',0):+.1f}% · contribution {child.get('contribution_pct',0):.1f}%", body))
        for leaf in child.get("children", []):
            story.append(Paragraph(f"&nbsp;&nbsp;&nbsp;– {leaf.get('label')}: {leaf.get('delta_pct',0):+.1f}%", small))

    # 6 Evidence
    story.append(Paragraph("6. Supporting Evidence & Methodology", h1))
    story.append(Paragraph("Evidence IDs attached to every major finding map to executable analytical methodology, SQL aggregation and aggregate outputs in the platform evidence vault. The report deliberately separates FACT, INSIGHT and HYPOTHESIS so causal claims are not presented as measured truth.", body))

    # 7 Recommendations
    story.append(Paragraph("7. Strategic Recommendations", h1))
    for i, rec in enumerate(dashboard_data.get("recommendations", []), 1):
        story.append(Paragraph(f"<b>{i:02d}. {rec.get('title')}</b>", body))
        story.append(Paragraph(f"{rec.get('recommendation')}<br/><b>Why:</b> {rec.get('why')}<br/><b>Impact sizing:</b> {rec.get('expected_impact_formatted')} · <b>Confidence:</b> {rec.get('confidence')} · <b>Timeframe:</b> {rec.get('implementation_timeframe')}", body))

    # 8 Scenario modeling
    story.append(Paragraph("8. What-If Scenario & Sensitivity Modeling", h1))
    story.append(Paragraph("Scenario modeling is intentionally interactive in the application. Users can change price/AOV, marketing spend, churn, delivery cost, COGS and return-rate levers; the deterministic simulator recalculates revenue, profit, margin, CAC and LTV using explicit elasticity assumptions. No scenario is represented here as a forecast.", body))

    # 9 Risks
    story.append(Paragraph("9. Risks, Assumptions & Governance", h1))
    story.append(Paragraph("The analytical engine uses deterministic calculations on the uploaded dataset. Correlation does not establish causation; scenario elasticity is directional; attribution quality depends on source-system completeness. Recommendations should be validated with controlled experiments, supplier contracts and operational capacity checks before deployment.", body))

    # 10 Roadmap
    story.append(Paragraph("10. Implementation Roadmap", h1))
    roadmap = ["0–30 days: validate the highest-impact cost and channel drivers;", "30–60 days: run controlled pricing, carrier and marketing allocation experiments;", "60–90 days: measure realized contribution impact and update the driver tree;", "90+ days: institutionalize recurring decision reviews and evidence-backed scenario planning."]
    for item in roadmap: story.append(Paragraph("• " + item, body))

    story.append(Spacer(1, 5*mm))
    story.append(Paragraph("Generated by Consulting in a Box · Deterministic analytics + governed AI interpretation · Currency: INR", small))
    doc.build(story)
    result = buffer.getvalue(); buffer.close(); return result
