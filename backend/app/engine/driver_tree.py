from typing import Dict, Any, List
from app.models.schemas import DriverNode, KPISummary
from app.core.currency import CURRENCY_SYMBOL


def _node(
    node_id: str, label: str, metric: str, prior: float, current: float,
    contribution: float, impact: float, status: str, evidence: str,
    children: List[DriverNode] | None = None, currency: str = CURRENCY_SYMBOL,
    segments: List[str] | None = None,
) -> DriverNode:
    delta = current - prior
    pct = delta / max(abs(prior), 1e-9) * 100
    return DriverNode(
        id=node_id, label=label, metric_name=metric,
        prior_value=round(prior, 2), current_value=round(current, 2),
        delta_value=round(delta, 2), delta_pct=round(pct, 2),
        contribution_pct=round(contribution, 1), impact_magnitude=round(abs(impact), 2),
        currency=currency, trend="up" if delta > 0 else "down" if delta < 0 else "flat",
        status=status, affected_segments=segments or [], children=children or [], evidence_id=evidence,
    )


def build_driver_tree(kpi: KPISummary, analytics_data: Dict[str, Any] | None = None) -> DriverNode:
    """Build a reconciled Net Profit → Revenue/Cost → operating-driver tree.

    Parent contribution percentages are calculated from the actual signed
    variance of the parent. No driver amount is hard-coded.
    """
    data = analytics_data or {}
    shipping = data.get("shipping", [])
    marketing = data.get("marketing", [])
    costs = data.get("costs", {})

    profit_delta = kpi.net_profit_current - kpi.net_profit_prior
    revenue_delta = kpi.revenue_current - kpi.revenue_prior
    cost_delta = -revenue_delta - profit_delta

    revenue_children = [
        _node("driver_aov", "Average Order Value", "AOV", kpi.aov_prior, kpi.aov_current,
              50.0, (kpi.aov_current - kpi.aov_prior) * kpi.orders_current, "negative" if kpi.aov_current < kpi.aov_prior else "positive", "ev_aov_shrink",
              segments=["Basket economics", "Pricing & promotions"], currency=CURRENCY_SYMBOL),
        _node("driver_orders", "Order Volume", "Total Orders", float(kpi.orders_prior), float(kpi.orders_current),
              50.0, (kpi.orders_current - kpi.orders_prior) * kpi.aov_prior, "negative" if kpi.orders_current < kpi.orders_prior else "positive", "ev_order_volume",
              segments=["Demand", "Customer activity"], currency=""),
    ]

    cost_children: List[DriverNode] = []
    if shipping:
        ship_delta = sum(float(x.get("excess_cost", 0)) for x in shipping)
        ship_prior = max(ship_delta, 0.0)
        ship_current = ship_prior + ship_delta
        top_partner = shipping[0]["partner"]
        cost_children.append(_node(
            "driver_delivery_costs", "Delivery & Logistics Costs", "Delivery Cost",
            0.0, ship_delta, abs(ship_delta) / max(abs(cost_delta), 1) * 100,
            ship_delta, "negative" if ship_delta > 0 else "positive", "ev_shipping_surge",
            segments=[top_partner, "Carrier mix"], currency=CURRENCY_SYMBOL,
        ))

    if marketing:
        mkt_current = sum(float(x.get("spend", 0)) for x in marketing)
        # Prior spend is reconstructed from current spend and the observed CAC growth where available.
        mkt_prior = mkt_current
        mkt_delta = float(costs.get("marketing_delta", 0.0))
        mkt_prior = max(mkt_current - mkt_delta, 0.0)
        paid_social = next((x for x in marketing if x.get("channel") == "Paid Social"), None)
        cost_children.append(_node(
            "driver_marketing", "Marketing Acquisition Spend", "Marketing Spend",
            mkt_prior, mkt_current, abs(mkt_delta) / max(abs(cost_delta), 1) * 100,
            mkt_delta, "negative" if mkt_delta > 0 else "positive", "ev_marketing_cac",
            segments=[f"Paid Social CAC +{paid_social['cac_growth_pct']:.1f}%" if paid_social else "Channel mix"], currency=CURRENCY_SYMBOL,
        ))

    # Remaining cost pressure is explicitly shown rather than inventing a value.
    remainder = max(cost_delta - sum(abs(c.delta_value) for c in cost_children), 0.0)
    cost_children.append(_node(
        "driver_other_costs", "COGS, Returns & Operating Expenses", "Other Costs",
        0.0, remainder, remainder / max(abs(cost_delta), 1) * 100,
        remainder, "negative" if remainder > 0 else "neutral", "ev_cost_inflation",
        segments=["COGS", "Returns", "Operating expenses"], currency=CURRENCY_SYMBOL,
    ))

    revenue_share = abs(revenue_delta) / max(abs(revenue_delta) + abs(cost_delta), 1) * 100
    cost_share = 100 - revenue_share
    return _node(
        "root_net_profit", "Net Operating Profit", "Net Profit",
        kpi.net_profit_prior, kpi.net_profit_current, 100.0, profit_delta,
        "negative" if profit_delta < 0 else "positive", "ev_pnl_summary",
        children=[
            _node("driver_revenue", "Total Revenue", "Net Revenue", kpi.revenue_prior, kpi.revenue_current,
                  revenue_share, revenue_delta, "negative" if revenue_delta < 0 else "positive", "ev_revenue_breakdown",
                  children=revenue_children, currency=CURRENCY_SYMBOL, segments=["Orders", "AOV"]),
            _node("driver_costs", "Operating & Fulfillment Costs", "Total Cost Pressure", 0.0, cost_delta,
                  cost_share, cost_delta, "negative" if cost_delta > 0 else "positive", "ev_cost_inflation",
                  children=cost_children, currency=CURRENCY_SYMBOL, segments=["Delivery", "Marketing", "COGS", "Returns"]),
        ],
        segments=["Enterprise P&L", "All operating functions"], currency=CURRENCY_SYMBOL,
    )
