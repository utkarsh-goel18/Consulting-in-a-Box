from __future__ import annotations
from typing import Any, Dict, List
from app.core.currency import CURRENCY_SYMBOL
from app.models.schemas import DriverNode, KPISummary

def _pct(current: float, prior: float) -> float:
    return round((current - prior) / max(abs(prior), 1e-9) * 100, 1)

def _contribution(impact: float, total_abs: float) -> float:
    return round(abs(impact) / max(total_abs, 1e-9) * 100, 1)

def _node(node_id: str, label: str, metric: str, prior: float, current: float, impact: float, total_abs: float, *, children: List[DriverNode] | None = None, evidence_id: str | None = None, status: str | None = None) -> DriverNode:
    return DriverNode(
        id=node_id, label=label, metric_name=metric,
        prior_value=round(prior, 2), current_value=round(current, 2), delta_value=round(impact, 2),
        delta_pct=_pct(current, prior), contribution_pct=_contribution(impact, total_abs),
        impact_magnitude=round(abs(impact), 2), currency=CURRENCY_SYMBOL,
        trend="up" if current > prior else "down" if current < prior else "flat",
        status=status or ("negative" if impact < 0 else "positive" if impact > 0 else "neutral"),
        affected_segments=[], children=children or [], evidence_id=evidence_id,
    )

def build_driver_tree(kpi: KPISummary, analytics_data: Dict[str, Any] | None = None) -> DriverNode:
    """Build a profit driver tree whose branches reconcile to the P&L bridge."""
    data = analytics_data or {}
    costs = data.get("costs", {})
    cost_items: list[tuple[str, float, float, float]] = []
    for name, values in costs.items():
        prior = float(values.get("prior", 0)) if isinstance(values, dict) else float(values[0])
        current = float(values.get("current", 0)) if isinstance(values, dict) else float(values[1])
        cost_items.append((name, prior, current, -(current - prior)))
    revenue_impact = kpi.revenue_current - kpi.revenue_prior
    cost_impact = sum(item[3] for item in cost_items)
    root_delta = kpi.net_profit_current - kpi.net_profit_prior
    residual = root_delta - revenue_impact - cost_impact
    top_total = abs(revenue_impact) + abs(cost_impact) + abs(residual)

    volume_effect = (kpi.orders_current - kpi.orders_prior) * kpi.aov_prior
    aov_effect = (kpi.aov_current - kpi.aov_prior) * kpi.orders_prior
    interaction = (kpi.orders_current - kpi.orders_prior) * (kpi.aov_current - kpi.aov_prior)
    revenue_abs = abs(volume_effect) + abs(aov_effect) + abs(interaction) or 1
    revenue_children = [
        _node("drv_orders", "Order volume", "Orders", kpi.orders_prior, kpi.orders_current, volume_effect, revenue_abs, evidence_id="ev_order_volume"),
        _node("drv_aov", "Average order value", "AOV", kpi.aov_prior, kpi.aov_current, aov_effect, revenue_abs, evidence_id="ev_aov_shrink"),
    ]
    if abs(interaction) > 0.01:
        revenue_children.append(_node("drv_volume_aov_interaction", "Volume × AOV interaction", "Revenue bridge interaction", 0, interaction, interaction, revenue_abs, evidence_id="ev_revenue_breakdown", status="neutral"))
    revenue_node = _node("drv_revenue", "Revenue change", "Net Revenue", kpi.revenue_prior, kpi.revenue_current, revenue_impact, top_total, children=revenue_children, evidence_id="ev_revenue_breakdown")

    evidence_map = {"COGS": "ev_cost_inflation", "Delivery Costs": "ev_shipping_surge", "Marketing Spend": "ev_marketing_cac", "Operating Expenses": "ev_cost_inflation", "Returns & Reverse Logistics": "ev_returns_breakdown"}
    cost_abs = sum(abs(item[3]) for item in cost_items) or 1
    cost_children = [_node(f"drv_cost_{name.lower().replace(' ', '_').replace('&', 'and')}", name, name, prior, current, impact, cost_abs, evidence_id=evidence_map.get(name)) for name, prior, current, impact in cost_items]
    prior_cost_total = sum(item[1] for item in cost_items)
    current_cost_total = sum(item[2] for item in cost_items)
    cost_node = _node("drv_costs", "Total cost pressure", "Total Costs", prior_cost_total, current_cost_total, cost_impact, top_total, children=cost_children, evidence_id="ev_cost_inflation")

    children = [revenue_node, cost_node]
    if abs(residual) > 0.01:
        children.append(_node("drv_reconciliation", "Other / reconciliation", "Unallocated P&L variance", 0, residual, residual, top_total, evidence_id="ev_pnl_summary", status="neutral"))
    return _node("root_net_profit", "Net operating profit", "Net Profit", kpi.net_profit_prior, kpi.net_profit_current, root_delta, top_total, children=children, evidence_id="ev_pnl_summary")
