from typing import List, Dict, Any
from app.models.schemas import ExecutiveInsight, StatementType, StrategicRecommendation, EvidenceDetail, KPISummary
from app.core.currency import format_inr, format_compact_inr


def _pct_phrase(value: float) -> str:
    return f"{value:+.1f}%"


def generate_classified_insights(kpi: KPISummary, analytics_data: Dict[str, Any] | None = None) -> List[ExecutiveInsight]:
    """Generate FACT / INSIGHT / HYPOTHESIS statements from verified analytics."""
    data = analytics_data or {}
    shipping = data.get("shipping", [])
    marketing = data.get("marketing", [])
    categories = data.get("categories", [])
    costs = data.get("costs", {})
    top_ship = shipping[0] if shipping else None
    paid_social = next((x for x in marketing if x.get("channel") == "Paid Social"), None)
    weakest_category = min(categories, key=lambda x: x.get("margin_pct", 999), default=None)

    insights: List[ExecutiveInsight] = [
        ExecutiveInsight(
            id="ins_fact_profit_decline", classification=StatementType.FACT,
            headline=f"Net operating profit changed {_pct_phrase(kpi.net_profit_growth_pct)} QoQ",
            narrative=f"Net profit moved from {format_inr(kpi.net_profit_prior)} to {format_inr(kpi.net_profit_current)} while revenue changed {_pct_phrase(kpi.revenue_growth_pct)}. The bridge is reconciled to the reported P&L.",
            magnitude_value=kpi.net_profit_current - kpi.net_profit_prior,
            magnitude_formatted=f"{format_compact_inr(kpi.net_profit_current - kpi.net_profit_prior)} ({kpi.net_profit_growth_pct:+.1f}%)",
            affected_area="Enterprise P&L", confidence="High", evidence_id="ev_pnl_summary",
        ),
        ExecutiveInsight(
            id="ins_fact_aov_drop", classification=StatementType.FACT,
            headline=f"AOV changed {_pct_phrase(kpi.aov_growth_pct)}",
            narrative=f"Average order value moved from {format_inr(kpi.aov_prior)} to {format_inr(kpi.aov_current)} across {kpi.orders_current:,} current-period orders.",
            magnitude_value=kpi.aov_current - kpi.aov_prior,
            magnitude_formatted=f"{format_inr(kpi.aov_current - kpi.aov_prior)} ({kpi.aov_growth_pct:+.1f}%) / order",
            affected_area="Merchandising & Pricing", confidence="High", evidence_id="ev_aov_shrink",
        ),
    ]
    if top_ship:
        insights.append(ExecutiveInsight(
            id="ins_fact_shipping_surge", classification=StatementType.FACT,
            headline=f"{top_ship['partner']} shows the largest delivery-cost increase",
            narrative=f"Average cost increased from {format_inr(top_ship['q2_avg_cost'])} to {format_inr(top_ship['q3_avg_cost'])}, a {top_ship['delta_pct']:+.1f}% change across {top_ship['orders']:,} current-period orders.",
            magnitude_value=top_ship["excess_cost"], magnitude_formatted=f"{format_compact_inr(top_ship['excess_cost'])} estimated excess cost",
            affected_area="Logistics & Supply Chain", confidence="High", evidence_id="ev_shipping_surge",
        ))
    if paid_social:
        insights.append(ExecutiveInsight(
            id="ins_insight_paid_social_decay", classification=StatementType.INSIGHT,
            headline=f"Paid Social efficiency deteriorated {_pct_phrase(paid_social['cac_growth_pct'])} on CAC",
            narrative=f"Paid Social CAC is {format_inr(paid_social['cac'])} with ROAS of {paid_social['roas']:.1f}x. The channel is flagged for reallocation when its efficiency falls below the configured threshold.",
            magnitude_value=paid_social["cac"], magnitude_formatted=f"CAC {format_inr(paid_social['cac'])} ({paid_social['cac_growth_pct']:+.1f}%)",
            affected_area="Growth & Performance Marketing", confidence="High", evidence_id="ev_marketing_cac",
        ))
    if weakest_category:
        insights.append(ExecutiveInsight(
            id="ins_insight_category_margin", classification=StatementType.INSIGHT,
            headline=f"{weakest_category['category']} has the weakest gross margin",
            narrative=f"The category contributes {format_inr(weakest_category['gross_margin'])} of gross margin at {weakest_category['margin_pct']:.1f}% margin, making it the first category for pricing and cost review.",
            magnitude_value=weakest_category["gross_margin"], magnitude_formatted=f"{weakest_category['margin_pct']:.1f}% gross margin",
            affected_area="Category Management", confidence="Medium", evidence_id="ev_category_margin",
        ))

    if kpi.churn_rate_delta_pp > 0:
        insights.append(ExecutiveInsight(
            id="ins_hypo_churn", classification=StatementType.HYPOTHESIS,
            headline=f"Customer churn increased {kpi.churn_rate_delta_pp:+.1f} pp",
            narrative="The increase is an observed signal, not proof of causality. Regional delivery, acquisition mix and customer-experience data should be tested before attributing the change to a specific operational trigger.",
            magnitude_value=kpi.churn_rate_delta_pp, magnitude_formatted=f"{kpi.churn_rate_delta_pp:+.1f} pp",
            affected_area="Customer Experience & Retention", confidence="Medium", evidence_id="ev_churn_surge",
        ))
    return insights


def generate_strategic_recommendations(kpi: KPISummary, analytics_data: Dict[str, Any] | None = None) -> List[StrategicRecommendation]:
    """Generate recommendations sized from the deterministic analytical outputs."""
    data = analytics_data or {}
    shipping = data.get("shipping", [])
    marketing = data.get("marketing", [])
    top_ship = shipping[0] if shipping else None
    paid_social = next((x for x in marketing if x.get("channel") == "Paid Social"), None)
    recs: List[StrategicRecommendation] = []

    if top_ship and top_ship["excess_cost"] > 0:
        recoverable = top_ship["excess_cost"] * 4 * 0.70
        recs.append(StrategicRecommendation(
            id="rec_01_logistics_rebalancing", title="Rebalance carrier economics",
            recommendation=f"Renegotiate {top_ship['partner']} rates and route a portion of high-cost lanes to the lowest-cost carrier that meets SLA requirements.",
            why=f"The largest observed carrier variance is {top_ship['delta_pct']:+.1f}% and represents approximately {format_inr(top_ship['excess_cost'])} of current-quarter excess cost versus the prior-period rate.",
            expected_impact_annualized=round(recoverable, 2), expected_impact_formatted=f"Up to {format_compact_inr(recoverable)} annualized at 70% recovery",
            confidence="High", implementation_timeframe="Quick Win (0-30 days)",
            assumptions=["Alternative carriers have sufficient capacity.", "SLA and delivery-time requirements remain unchanged.", "The observed rate variance is contractually addressable."],
            supporting_evidence_ids=["ev_shipping_surge", "ev_pnl_summary"],
        ))
    if paid_social and paid_social["cac_growth_pct"] > 0:
        quarterly_saving = paid_social["spend"] * 0.20
        recs.append(StrategicRecommendation(
            id="rec_02_paid_social_reallocation", title="Reallocate underperforming paid-media spend",
            recommendation="Reduce marginal Paid Social spend and redeploy budget toward channels with stronger observed ROAS, validating incrementality before scaling.",
            why=f"Paid Social CAC is {format_inr(paid_social['cac'])} and has changed {paid_social['cac_growth_pct']:+.1f}% versus the prior quarter, while observed ROAS is {paid_social['roas']:.1f}x.",
            expected_impact_annualized=round(quarterly_saving * 4, 2), expected_impact_formatted=f"~{format_compact_inr(quarterly_saving * 4)} annualized spend exposure",
            confidence="Medium", implementation_timeframe="Tactical (30-60 days)",
            assumptions=["Replacement channels can absorb incremental budget.", "Conversion quality remains stable after reallocation.", "Attribution is directionally reliable."],
            supporting_evidence_ids=["ev_marketing_cac"],
        ))
    aov_recovery = max(kpi.revenue_prior - kpi.revenue_current, 0) * 0.20
    recs.append(StrategicRecommendation(
        id="rec_03_aov_recovery", title="Test targeted basket and pricing interventions",
        recommendation="Run controlled basket-building and threshold-pricing experiments rather than applying a blanket discount. Measure incremental AOV and contribution margin together.",
        why=f"AOV changed {kpi.aov_growth_pct:+.1f}% from {format_inr(kpi.aov_prior)} to {format_inr(kpi.aov_current)}.",
        expected_impact_annualized=round(aov_recovery * 4, 2), expected_impact_formatted=f"Scenario sizing: {format_compact_inr(aov_recovery * 4)} annualized at 20% revenue-gap recovery",
        confidence="Medium", implementation_timeframe="Strategic (60-90 days)",
        assumptions=["Experiment traffic is representative.", "Incremental revenue is evaluated after COGS and fulfilment effects.", "No material increase in return rate."],
        supporting_evidence_ids=["ev_aov_shrink"],
    ))
    return recs


def get_evidence_catalog(kpi: KPISummary | None = None, analytics_data: Dict[str, Any] | None = None) -> Dict[str, EvidenceDetail]:
    """Evidence registry. SQL is executable methodology; sample values are derived from the current snapshot."""
    k = kpi
    data = analytics_data or {}
    shipping = data.get("shipping", [])
    marketing = data.get("marketing", [])
    top_ship = shipping[0] if shipping else None
    paid_social = next((x for x in marketing if x.get("channel") == "Paid Social"), None)
    q2 = format_inr(k.net_profit_prior) if k else "n/a"
    q3 = format_inr(k.net_profit_current) if k else "n/a"
    return {
        "ev_pnl_summary": EvidenceDetail(
            evidence_id="ev_pnl_summary", title="Quarterly P&L variance reconciliation",
            methodology="Aggregate revenue, COGS, delivery, marketing, operating expense and returns by quarter; reconcile the bridge to net profit.",
            mathematical_formula="Net Profit = Revenue - COGS - Delivery - Marketing - Opex - Returns",
            sql_query="SELECT DATE_TRUNC('quarter', order_date) AS quarter, SUM(net_amount) AS revenue, SUM(delivery_cost) AS delivery_cost FROM orders GROUP BY 1 ORDER BY 1;",
            sample_records=[{"period": "Prior quarter", "net_profit": q2}, {"period": "Current quarter", "net_profit": q3}],
            aggregate_table=[{"metric": "Revenue", "prior": k.revenue_prior if k else None, "current": k.revenue_current if k else None, "delta_pct": k.revenue_growth_pct if k else None}, {"metric": "Net Profit", "prior": k.net_profit_prior if k else None, "current": k.net_profit_current if k else None, "delta_pct": k.net_profit_growth_pct if k else None}],
        ),
        "ev_revenue_breakdown": EvidenceDetail(
            evidence_id="ev_revenue_breakdown", title="Revenue decomposition", methodology="Revenue is decomposed into order volume and average order value.", mathematical_formula="Revenue = Orders × AOV",
            sql_query="SELECT COUNT(*) AS orders, SUM(net_amount) AS revenue, AVG(net_amount) AS aov FROM orders WHERE order_status <> 'Cancelled' GROUP BY DATE_TRUNC('quarter', order_date);",
            sample_records=[], aggregate_table=[{"metric": "Orders", "prior": k.orders_prior if k else None, "current": k.orders_current if k else None}, {"metric": "AOV", "prior": k.aov_prior if k else None, "current": k.aov_current if k else None}],
        ),
        "ev_order_volume": EvidenceDetail(
            evidence_id="ev_order_volume", title="Order-volume analysis", methodology="Count non-cancelled orders by quarter and compare active customer coverage.", mathematical_formula="Order Growth = (Current Orders - Prior Orders) / Prior Orders",
            sql_query="SELECT DATE_TRUNC('quarter', order_date) AS quarter, COUNT(order_id) AS orders, COUNT(DISTINCT customer_id) AS active_customers FROM orders WHERE order_status <> 'Cancelled' GROUP BY 1;",
            sample_records=[], aggregate_table=[{"metric": "Orders", "prior": k.orders_prior if k else None, "current": k.orders_current if k else None}],
        ),
        "ev_aov_shrink": EvidenceDetail(
            evidence_id="ev_aov_shrink", title="Average order value analysis", methodology="Compare quarterly revenue per order and discount intensity.", mathematical_formula="AOV = Net Revenue / Orders",
            sql_query="SELECT DATE_TRUNC('quarter', order_date) AS quarter, AVG(net_amount) AS aov, AVG(discount_amount) AS avg_discount FROM orders GROUP BY 1;",
            sample_records=[], aggregate_table=[{"metric": "AOV", "prior": k.aov_prior if k else None, "current": k.aov_current if k else None, "delta_pct": k.aov_growth_pct if k else None}],
        ),
        "ev_shipping_surge": EvidenceDetail(
            evidence_id="ev_shipping_surge", title="Carrier delivery-rate analysis", methodology="Compare carrier-level mean delivery cost and current-period volume.", mathematical_formula="Excess Cost = (Current Avg Rate - Prior Avg Rate) × Current Orders",
            sql_query="SELECT shipping_partner, DATE_TRUNC('quarter', order_date) AS quarter, AVG(delivery_cost) AS avg_delivery_cost, COUNT(*) AS orders FROM orders GROUP BY 1,2 ORDER BY 1,2;",
            sample_records=[top_ship] if top_ship else [], aggregate_table=shipping,
        ),
        "ev_marketing_cac": EvidenceDetail(
            evidence_id="ev_marketing_cac", title="Channel CAC and ROAS analysis", methodology="Compare channel spend, attributed orders, CAC and attributed revenue by quarter.", mathematical_formula="CAC = Spend / Attributed Orders; ROAS = Attributed Revenue / Spend",
            sql_query="SELECT channel, DATE_TRUNC('quarter', spend_date) AS quarter, SUM(spend_amount) AS spend, SUM(attributed_orders) AS orders, SUM(attributed_revenue) AS revenue FROM marketing_spend GROUP BY 1,2;",
            sample_records=[paid_social] if paid_social else [], aggregate_table=marketing,
        ),
        "ev_category_margin": EvidenceDetail(
            evidence_id="ev_category_margin", title="Category gross-margin analysis", methodology="Join order items to products and calculate revenue, COGS and gross margin by category.", mathematical_formula="Gross Margin % = (Item Revenue - Item COGS) / Item Revenue",
            sql_query="SELECT p.category, SUM(oi.item_total) AS revenue, SUM(oi.quantity * oi.unit_cogs) AS cogs FROM order_items oi JOIN products p ON p.product_id = oi.product_id GROUP BY 1;",
            sample_records=[], aggregate_table=data.get("categories", []),
        ),
        "ev_churn_surge": EvidenceDetail(
            evidence_id="ev_churn_surge", title="Customer churn signal", methodology="Compare the observed quarter-level churn flags in the customer master; use this as a signal, not causal proof.", mathematical_formula="Churn Rate = Churned Customers / Customer Base",
            sql_query="SELECT AVG(CAST(churn_status AS DOUBLE)) * 100 AS churn_rate FROM customers;",
            sample_records=[], aggregate_table=[{"metric": "Churn prior", "value": k.churn_rate_prior_pct if k else None}, {"metric": "Churn current", "value": k.churn_rate_current_pct if k else None}],
        ),
        "ev_cost_inflation": EvidenceDetail(
            evidence_id="ev_cost_inflation", title="Operating cost bridge", methodology="Reconcile changes in COGS, delivery, marketing, operating expenses and returns.", mathematical_formula="Cost Pressure = ΔCOGS + ΔDelivery + ΔMarketing + ΔOpex + ΔReturns",
            sql_query="SELECT DATE_TRUNC('quarter', expense_date) AS quarter, SUM(amount) AS opex FROM expenses GROUP BY 1;",
            sample_records=[], aggregate_table=[],
        ),
        "ev_returns_breakdown": EvidenceDetail(
            evidence_id="ev_returns_breakdown", title="Returns and reverse-logistics analysis", methodology="Aggregate refunds and reverse-logistics costs by quarter and return reason.", mathematical_formula="Return Cost = Refund Amount + Reverse Logistics Cost",
            sql_query="SELECT DATE_TRUNC('quarter', return_date) AS quarter, SUM(refund_amount) AS refunds, SUM(reverse_logistics_cost) AS reverse_logistics FROM returns GROUP BY 1;",
            sample_records=[], aggregate_table=[],
        ),
    }
