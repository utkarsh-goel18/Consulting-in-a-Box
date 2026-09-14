from __future__ import annotations

from typing import Any, Dict, List

from app.models.schemas import DriverNode, KPISummary
from app.core.currency import CURRENCY_SYMBOL


def _pct(current: float, prior: float) -> float:
    return round((current - prior) / max(abs(prior), 1e-9) * 100, 1)


def _contribution(impact: float, total_abs: float) -> float:
    return round(abs(impact) / max(total_abs, 1e-9) * 100, 1)


def _node(node_id: str, label: str, metric: str, prior: float, current: float, impact: float, total_abs: float, *, children: List[DriverNode] | None = None, evidence_id: str | None = None, status: str | None = None) -> DriverNode:
    trend = "up" if current > prior else "down" if current < prior else "flat"
    return DriverNode(
        id=node_id,
        label=label,
        metric_name=metric,
        prior_value=round(prior, 2),
        current_value=round(current, 2),
        delta_value=round(impact, 2),
        delta_pct=_pct(current, prior),
        contribution_pct=_contribution(impact, total_abs),
        impact_magnitude=round(abs(impact), 2),
        currency=CURRENCY_SYMBOL,
        trend=trend,
        status=status or ("critical" if impact < 0 else "favorable" if impact > 0 else "neutral"),
        children=children or [],
        evidence_id=evidence_id,
    )


def build_driver_tree(kpi: KPISummary, analytics_data: Dict[str, Any] | None = None) -> DriverNode:
    """Build a reconciled profit driver tree from the deterministic P&L bridge.

    First-level profit impacts sum exactly to the observed net-profit change;
    revenue and cost branches then decompose their own impacts into auditable
    sub-drivers, with residuals used explicitly for reconciliation.
    """
    data = analytics_data or {}
    costs = data.get("costs", {})
    revenue_impact = kpi.revenue_current - kpi.revenue_prior
    cost_items = []
    for name, values in costs.items():
        if isinstance(values, dict):
            prior, current = float(values.get("prior", 0)), float(values.get("current", 0))
        else:
            prior, current = values
        cost_items.append((name, prior, current, -(current - prior)))
    cost_impact = sum(item[3] for item in cost_items)
    root_delta = kpi.net_profit_current - kpi.net_profit_prior
    residual = root_delta - (revenue_impact + cost_impact)
    top_total = abs(revenue_impact) + abs(cost_impact) + abs(residual)

    # Revenue decomposition: volume + AOV + interaction exactly reconciles revenue change.
    volume_effect = (kpi.orders_current - kpi.orders_prior) * kpi.aov_prior
    aov_effect = (kpi.aov_current - kpi.aov_prior) * kpi.orders_prior
    interaction = (kpi.orders_current - kpi.orders_prior) * (kpi.aov_current - kpi.aov_prior)
    revenue_abs = abs(volume_effect) + abs(aov_effect) + abs(interaction)
    revenue_children = [
        _node("drv_orders", "Order volume", "Orders", kpi.orders_prior, kpi.orders_current, volume_effect, revenue_abs, evidence_id="ev_order_volume"),
        _node("drv_aov", "Average order value", "AOV", kpi.aov_prior, kpi.aov_current, aov_effect, revenue_abs, evidence_id="ev_aov_shrink"),
    ]
    if abs(interaction) > 0.01:
        revenue_children.append(_node("drv_volume_aov_interaction", "Volume × AOV interaction", "Revenue bridge interaction", 0, interaction, interaction, revenue_abs, evidence_id="ev_revenue_breakdown", status="neutral"))

    revenue_node = _node("drv_revenue", "Revenue change", "Net Revenue", kpi.revenue_prior, kpi.revenue_current, revenue_impact, top_total, children=revenue_children, evidence_id="ev_revenue_breakdown")

    # Cost decomposition: each cost line is a direct profit impact.
    cost_abs = sum(abs(item[3]) for item in cost_items) or 1
    cost_children = [
        _node(f"drv_cost_{name.lower().replace(' ', '_').replace('&', 'and')}", name, name, prior, current, impact, cost_abs,
              evidence_id={"COGS": "ev_cost_inflation", "Delivery Costs": "ev_shipping_surge", "Marketing Spend": "ev_marketing_cac", "Operating Expenses": "ev_cost_inflation", "Returns & Reverse Logistics": "ev_returns_breakdown"}.get(name))
        for name, prior, current, impact in cost_items
    ]
    cost_node = _node("drv_costs", "Total cost pressure", "Total Costs", 0, -cost_impact, cost_impact, top_total, children=cost_children, evidence_id="ev_cost_inflation")

    children = [revenue_node, cost_node]
    if abs(residual) > 0.01:
        children.append(_node("drv_reconciliation", "Other / reconciliation", "Unallocated P&L variance", 0, residual, residual, top_total, evidence_id="ev_pnl_summary", status="neutral"))

    return _node("root_net_profit", "Net operating profit", "Net Profit", kpi.net_profit_prior, kpi.net_profit_current, root_delta, top_total, children=children, evidence_id="ev_pnl_summary")
