from typing import Dict, Any, List
from app.models.schemas import ScenarioLevers, ScenarioResult, MetricComparison, KPISummary

def run_what_if_simulation(kpi: KPISummary, levers: ScenarioLevers) -> ScenarioResult:
    """
    Simulates business performance under modified business parameters using
    microeconomic elasticity and financial sensitivity models.
    """
    # 1. Base parameters
    base_orders = float(kpi.orders_current)
    base_aov = float(kpi.aov_current)
    base_rev = float(kpi.revenue_current)
    base_customers = float(kpi.active_customers_current)
    base_mkt = float(kpi.cac_current * base_customers)
    base_delivery_cost_per_order = 48.20 # Average delivery cost per order
    base_del_total = base_delivery_cost_per_order * base_orders
    base_cogs = base_rev * 0.595
    base_opex = 670000.0
    base_returns = 235000.0
    base_churn = float(kpi.churn_rate_current_pct)
    base_cac = float(kpi.cac_current)
    
    # Base LTV = (AOV * Gross Margin % * Annual Orders) / Churn Rate
    base_gross_margin_pct = (base_rev - base_cogs) / max(base_rev, 1)
    base_annual_orders_per_cust = (base_orders / max(base_customers, 1)) * 4.0
    base_ltv = (base_aov * base_gross_margin_pct * base_annual_orders_per_cust) / max(base_churn / 100.0, 0.01)
    
    # Base Net Profit
    base_total_cost = base_cogs + base_del_total + base_mkt + base_opex + base_returns
    base_net_profit = base_rev - base_total_cost
    base_margin_pct = (base_net_profit / max(base_rev, 1)) * 100.0
    
    # 2. Apply Scenario Levers & Elasticities
    # Price elasticity of demand: e_d ~= -0.75 (modest elasticity in retail e-commerce)
    price_factor = 1.0 + (levers.price_change_pct / 100.0)
    order_elasticity_factor = 1.0 + (-0.75 * (levers.price_change_pct / 100.0))
    
    # Marketing spend change: spend elasticity of acquisition ~= 0.60
    mkt_spend_factor = 1.0 + (levers.marketing_spend_delta_pct / 100.0)
    cust_acquisition_factor = 1.0 + (0.60 * (levers.marketing_spend_delta_pct / 100.0))
    
    # Churn delta effect on customer base
    scenario_churn = max(1.0, base_churn + levers.churn_rate_delta_pp)
    churn_retention_multiplier = (100.0 - scenario_churn) / (100.0 - base_churn)
    
    # Calculate Scenario Metrics
    scenario_customers = base_customers * cust_acquisition_factor * churn_retention_multiplier
    scenario_orders = base_orders * order_elasticity_factor * (scenario_customers / base_customers)
    scenario_aov = base_aov * price_factor
    scenario_rev = scenario_orders * scenario_aov
    
    # COGS optimization
    scenario_cogs_rate = 0.595 * (1.0 + (levers.cogs_reduction_pct / 100.0))
    scenario_cogs = scenario_rev * scenario_cogs_rate
    scenario_gross_profit = scenario_rev - scenario_cogs
    scenario_gross_margin_pct = scenario_gross_profit / max(scenario_rev, 1)
    
    # Delivery cost lever
    scenario_delivery_cost_per_order = base_delivery_cost_per_order * (1.0 + (levers.delivery_cost_delta_pct / 100.0))
    scenario_del_total = scenario_delivery_cost_per_order * scenario_orders
    
    # Marketing spend
    scenario_mkt = base_mkt * mkt_spend_factor
    scenario_cac = scenario_mkt / max(scenario_customers, 1)
    
    # Returns reduction
    scenario_returns = base_returns * (1.0 + (levers.return_rate_delta_pp / 10.0))
    
    # Scenario Net Profit & Margin
    scenario_total_cost = scenario_cogs + scenario_del_total + scenario_mkt + base_opex + scenario_returns
    scenario_net_profit = scenario_rev - scenario_total_cost
    scenario_net_margin_pct = (scenario_net_profit / max(scenario_rev, 1)) * 100.0
    
    # Scenario LTV
    scenario_annual_orders = (scenario_orders / max(scenario_customers, 1)) * 4.0
    scenario_ltv = (scenario_aov * scenario_gross_margin_pct * scenario_annual_orders) / max(scenario_churn / 100.0, 0.01)

    # 3. Format comparisons
    def build_comp(name: str, base: float, sc: float, is_currency: bool = False, is_pct: bool = False) -> MetricComparison:
        abs_d = sc - base
        pct_d = ((sc - base) / max(abs(base), 0.01)) * 100.0
        
        if is_currency:
            fb = f"${base:,.0f}"
            fs = f"${sc:,.0f}"
            fd = f"{'+' if abs_d >= 0 else '-'}${abs(abs_d):,.0f} ({pct_d:+.1f}%)"
        elif is_pct:
            fb = f"{base:.1f}%"
            fs = f"{sc:.1f}%"
            fd = f"{abs_d:+.1f} pp ({pct_d:+.1f}%)"
        else:
            fb = f"{base:,.0f}"
            fs = f"{sc:,.0f}"
            fd = f"{abs_d:+,.0f} ({pct_d:+.1f}%)"
            
        positive = abs_d > 0 if name not in ["CAC", "Total Costs", "Delivery Cost / Order", "Churn Rate"] else abs_d < 0
        
        return MetricComparison(
            metric_name=name,
            base_value=round(base, 2),
            scenario_value=round(sc, 2),
            absolute_delta=round(abs_d, 2),
            percentage_delta=round(pct_d, 1),
            formatted_base=fb,
            formatted_scenario=fs,
            formatted_delta=fd,
            is_positive_trend=positive
        )

    metrics = {
        "Revenue": build_comp("Revenue", base_rev, scenario_rev, is_currency=True),
        "Gross Profit": build_comp("Gross Profit", base_rev - base_cogs, scenario_gross_profit, is_currency=True),
        "Net Profit": build_comp("Net Profit", base_net_profit, scenario_net_profit, is_currency=True),
        "Profit Margin": build_comp("Profit Margin", base_margin_pct, scenario_net_margin_pct, is_pct=True),
        "Orders": build_comp("Orders", base_orders, scenario_orders),
        "Customers": build_comp("Active Customers", base_customers, scenario_customers),
        "AOV": build_comp("Average Order Value", base_aov, scenario_aov, is_currency=True),
        "CAC": build_comp("Customer Acquisition Cost", base_cac, scenario_cac, is_currency=True),
        "LTV": build_comp("Customer Lifetime Value", base_ltv, scenario_ltv, is_currency=True)
    }
    
    # Waterfall breakdown of scenario impact on Net Profit
    profit_delta = scenario_net_profit - base_net_profit
    rev_impact = (scenario_rev - base_rev) * base_gross_margin_pct
    del_impact = -(scenario_del_total - base_del_total)
    mkt_impact = -(scenario_mkt - base_mkt)
    cogs_opt_impact = -(scenario_cogs - (scenario_rev * 0.595))
    
    waterfall = [
        {"lever": "Base Net Profit", "amount": round(base_net_profit, 0), "type": "total"},
        {"lever": "Pricing & Volume Net Effect", "amount": round(rev_impact, 0), "type": "positive" if rev_impact >= 0 else "negative"},
        {"lever": "Delivery Optimization", "amount": round(del_impact, 0), "type": "positive" if del_impact >= 0 else "negative"},
        {"lever": "Marketing Rebalancing", "amount": round(mkt_impact, 0), "type": "positive" if mkt_impact >= 0 else "negative"},
        {"lever": "COGS Direct Savings", "amount": round(cogs_opt_impact, 0), "type": "positive" if cogs_opt_impact >= 0 else "negative"},
        {"lever": "Simulated Net Profit", "amount": round(scenario_net_profit, 0), "type": "total"}
    ]
    
    # Executive narrative verdict
    verdict = (
        f"Implementing this simulated scenario is projected to generate an incremental ${abs(profit_delta):,.0f} "
        f"({'+' if profit_delta >= 0 else ''}{((scenario_net_profit - base_net_profit)/max(abs(base_net_profit),1))*100:.1f}%) "
        f"in quarterly operating profit, shifting net margin from {base_margin_pct:.1f}% to {scenario_net_margin_pct:.1f}%."
    )
    
    assumptions = [
        "Price elasticity of demand is modeled at -0.75 based on competitive category benchmarks.",
        "Marketing spend reductions reduce acquisition volume with diminishing sensitivity (0.60 exponent).",
        "Delivery renegotiations assume contracted volume minimums are sustained.",
        "Customer churn improvements assume immediate retention stabilization across active cohorts."
    ]

    return ScenarioResult(
        levers=levers,
        metrics=metrics,
        waterfall_breakdown=waterfall,
        executive_verdict=verdict,
        key_assumptions=assumptions
    )
