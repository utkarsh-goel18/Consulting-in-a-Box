import math
from typing import Dict, Any
from app.models.schemas import ScenarioLevers, ScenarioResult, MetricComparison, KPISummary
from app.core.currency import format_inr


def run_what_if_simulation(kpi: KPISummary, levers: ScenarioLevers, analytics_data: Dict[str, Any] | None = None) -> ScenarioResult:
    """Run a transparent deterministic sensitivity model from the verified base case."""
    data = analytics_data or {}
    costs = data.get("costs", {})
    shipping = data.get("shipping", [])

    base_orders = float(kpi.orders_current) if math.isfinite(float(kpi.orders_current)) else 1.0
    base_aov = float(kpi.aov_current) if math.isfinite(float(kpi.aov_current)) else 0.0
    base_rev = float(kpi.revenue_current) if math.isfinite(float(kpi.revenue_current)) else 0.0
    base_customers = float(kpi.active_customers_current) if math.isfinite(float(kpi.active_customers_current)) else 1.0
    base_cac = float(kpi.cac_current) if math.isfinite(float(kpi.cac_current)) else 0.0
    base_mkt = float(base_cac * base_customers)
    base_cogs = max(base_rev - (float(kpi.gross_profit_current) if math.isfinite(float(kpi.gross_profit_current)) else 0.0), 0.0)
    base_delivery = float(data.get("delivery_current", base_rev * 0.08))
    base_net_profit = float(kpi.net_profit_current) if math.isfinite(float(kpi.net_profit_current)) else 0.0
    base_opex_returns = max(base_rev - base_cogs - base_delivery - base_mkt - base_net_profit, 0.0)

    try:
        base_churn = float(kpi.churn_rate_current_pct)
        if not math.isfinite(base_churn) or base_churn <= 0:
            base_churn = 5.0
    except (TypeError, ValueError):
        base_churn = 5.0

    price_factor = 1.0 + levers.price_change_pct / 100.0
    volume_factor = max(0.25, 1.0 - 0.75 * levers.price_change_pct / 100.0)
    marketing_factor = max(0.1, 1.0 + levers.marketing_spend_delta_pct / 100.0)
    acquisition_factor = max(0.2, 1.0 + 0.60 * levers.marketing_spend_delta_pct / 100.0)
    scenario_churn = max(0.5, base_churn + levers.churn_rate_delta_pp)
    retention_factor = (100.0 - scenario_churn) / max(100.0 - base_churn, 1.0)

    scenario_customers = base_customers * acquisition_factor * retention_factor
    scenario_orders = base_orders * volume_factor * (scenario_customers / max(base_customers, 1.0))
    scenario_aov = base_aov * price_factor
    scenario_rev = scenario_orders * scenario_aov

    scenario_cogs = base_cogs * (scenario_rev / max(base_rev, 1.0)) * (1.0 + levers.cogs_reduction_pct / 100.0)
    scenario_delivery = base_delivery * (scenario_orders / max(base_orders, 1.0)) * (1.0 + levers.delivery_cost_delta_pct / 100.0)
    scenario_mkt = base_mkt * marketing_factor
    scenario_returns = base_opex_returns * (1.0 + levers.return_rate_delta_pp / 100.0)
    scenario_net_profit = scenario_rev - scenario_cogs - scenario_delivery - scenario_mkt - scenario_returns
    base_margin = base_net_profit / max(base_rev, 1.0) * 100.0
    scenario_margin = scenario_net_profit / max(scenario_rev, 1.0) * 100.0
    scenario_cac = scenario_mkt / max(scenario_customers, 1.0)
    base_margin_rate = (float(kpi.gross_profit_current) if math.isfinite(float(kpi.gross_profit_current)) else 0.0) / max(base_rev, 1.0)
    base_frequency = base_orders / max(base_customers, 1.0)
    scenario_frequency = scenario_orders / max(scenario_customers, 1.0)
    base_ltv = base_aov * base_margin_rate * (base_frequency * 4) / max(base_churn / 100, 0.01)
    scenario_ltv = scenario_aov * ((scenario_rev - scenario_cogs) / max(scenario_rev, 1.0)) * (scenario_frequency * 4) / max(scenario_churn / 100, 0.01)

    def build_comp(name: str, base: float, scenario: float, currency: bool = False, pct: bool = False) -> MetricComparison:
        b = float(base) if math.isfinite(float(base)) else 0.0
        s = float(scenario) if math.isfinite(float(scenario)) else 0.0
        delta = s - b
        delta_pct = delta / max(abs(b), 0.01) * 100
        if not math.isfinite(delta_pct):
            delta_pct = 0.0
        if currency:
            fb, fs, fd = format_inr(b), format_inr(s), f"{'+' if delta >= 0 else '-'}{format_inr(abs(delta))} ({delta_pct:+.1f}%)"
        elif pct:
            fb, fs, fd = f"{b:.1f}%", f"{s:.1f}%", f"{delta:+.1f} pp ({delta_pct:+.1f}%)"
        else:
            fb, fs, fd = f"{b:,.0f}", f"{s:,.0f}", f"{delta:+,.0f} ({delta_pct:+.1f}%)"
        cost_metric = name in {"CAC", "Total Costs", "Delivery Cost / Order", "Churn Rate"}
        positive = delta < 0 if cost_metric else delta > 0
        return MetricComparison(metric_name=name, base_value=round(b, 2), scenario_value=round(s, 2), absolute_delta=round(delta, 2), percentage_delta=round(delta_pct, 1), formatted_base=fb, formatted_scenario=fs, formatted_delta=fd, is_positive_trend=positive)

    metrics = {
        "Revenue": build_comp("Revenue", base_rev, scenario_rev, currency=True),
        "Gross Profit": build_comp("Gross Profit", kpi.gross_profit_current, scenario_rev - scenario_cogs, currency=True),
        "Net Profit": build_comp("Net Profit", kpi.net_profit_current, scenario_net_profit, currency=True),
        "Profit Margin": build_comp("Profit Margin", base_margin, scenario_margin, pct=True),
        "Orders": build_comp("Orders", base_orders, scenario_orders),
        "Customers": build_comp("Active Customers", base_customers, scenario_customers),
        "AOV": build_comp("Average Order Value", base_aov, scenario_aov, currency=True),
        "CAC": build_comp("Customer Acquisition Cost", kpi.cac_current, scenario_cac, currency=True),
        "LTV": build_comp("Customer Lifetime Value", base_ltv, scenario_ltv, currency=True),
    }

    waterfall = [
        {"lever": "Base Net Profit", "amount": round(kpi.net_profit_current, 0), "type": "total"},
        {"lever": "Pricing & Volume", "amount": round((scenario_rev - base_rev) * base_margin_rate, 0), "type": "positive" if scenario_rev >= base_rev else "negative"},
        {"lever": "Delivery Cost", "amount": round(-(scenario_delivery - base_delivery), 0), "type": "positive" if scenario_delivery <= base_delivery else "negative"},
        {"lever": "Marketing Spend", "amount": round(-(scenario_mkt - base_mkt), 0), "type": "positive" if scenario_mkt <= base_mkt else "negative"},
        {"lever": "COGS & Returns", "amount": round(-(scenario_cogs - base_cogs) - (scenario_returns - base_opex_returns), 0), "type": "positive" if scenario_cogs + scenario_returns <= base_cogs + base_opex_returns else "negative"},
        {"lever": "Scenario Net Profit", "amount": round(scenario_net_profit, 0), "type": "total"},
    ]
    profit_delta = scenario_net_profit - kpi.net_profit_current
    verdict = f"The modeled scenario changes quarterly operating profit by {format_inr(profit_delta)} ({profit_delta / max(abs(kpi.net_profit_current), 1) * 100:+.1f}%), moving net margin from {base_margin:.1f}% to {scenario_margin:.1f}%."
    assumptions = [
        "Price elasticity is modeled at -0.75 for order volume.",
        "Marketing acquisition elasticity is modeled at 0.60.",
        "Churn, delivery and return levers are applied linearly to the verified current-period base.",
        "Scenario outputs are directional sensitivities, not forecasts or causal estimates.",
    ]
    return ScenarioResult(levers=levers, metrics=metrics, waterfall_breakdown=waterfall, executive_verdict=verdict, key_assumptions=assumptions)
