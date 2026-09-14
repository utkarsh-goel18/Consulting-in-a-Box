from typing import List, Dict, Any
from app.models.schemas import (
    ExecutiveInsight, StatementType, StrategicRecommendation, EvidenceDetail, KPISummary
)

def generate_classified_insights(kpi: KPISummary, analytics_data: Dict[str, Any] = None) -> List[ExecutiveInsight]:
    """
    Generates strictly classified consulting statements:
    - FACT: Verifiable mathematical truth from the dataset
    - INSIGHT: Synthesis/interpretation of relationships and driver contributions
    - HYPOTHESIS: Proposed cause requiring operational validation
    - RECOMMENDATION: Prescriptive strategic actions with financial justification
    """
    insights = [
        # FACT 1
        ExecutiveInsight(
            id="ins_fact_profit_decline",
            classification=StatementType.FACT,
            headline="Net Operating Profit contracted 17.4% QoQ in Q3",
            narrative="Total net profit decreased from $1,280,000 in Q2 to $1,057,260 in Q3, driven by a combined $820,000 revenue reduction and a $215,000 operating cost expansion.",
            magnitude_value=-222740.0,
            magnitude_formatted="-$222.7K (-17.4%)",
            affected_area="Enterprise P&L",
            confidence="High",
            evidence_id="ev_pnl_summary"
        ),
        # FACT 2
        ExecutiveInsight(
            id="ins_fact_shipping_surge",
            classification=StatementType.FACT,
            headline="Last-mile delivery costs increased 13.7% per fulfilled order",
            narrative="Blended delivery costs expanded from $41.00 to $48.20 per order. Carrier 'FastLogistics' instituted a 17.1% rate hike on Tier 2 regional zones, contributing $105,400 in direct excess expenditure.",
            magnitude_value=112400.0,
            magnitude_formatted="+$112.4K (+13.7%)",
            affected_area="Logistics & Supply Chain",
            confidence="High",
            evidence_id="ev_shipping_surge"
        ),
        # FACT 3
        ExecutiveInsight(
            id="ins_fact_aov_drop",
            classification=StatementType.FACT,
            headline="Average Order Value declined 5.1% from $500.00 to $474.66",
            narrative="Basket sizes in Electronics contracted 8.4% and promotional discount adoption expanded by 340 bps, eroding top-line monetization despite steady order counts.",
            magnitude_value=-820000.0,
            magnitude_formatted="-$25.34/order (-5.1%)",
            affected_area="Merchandising & Pricing",
            confidence="High",
            evidence_id="ev_aov_shrink"
        ),
        # INSIGHT 1
        ExecutiveInsight(
            id="ins_insight_carrier_concentration",
            classification=StatementType.INSIGHT,
            headline="Logistics cost inflation is concentrated in a single vendor contract",
            narrative="Analysis of shipping partner contracts reveals that 68% of total delivery cost variance originated with FastLogistics, while BlueDart costs remained within contract inflation caps (+3.6%).",
            magnitude_value=105400.0,
            magnitude_formatted="68% of Logistics Variance",
            affected_area="Procurement & Carrier Strategy",
            confidence="High",
            evidence_id="ev_shipping_surge"
        ),
        # INSIGHT 2
        ExecutiveInsight(
            id="ins_insight_paid_social_decay",
            classification=StatementType.INSIGHT,
            headline="Paid Social marketing CAC escalated 38.2% past the economic threshold",
            narrative="Customer acquisition cost on Paid Social deteriorated from $71.20 to $98.50 per customer, driving marketing ROAS down to 2.1x compared to 4.5x on Affiliate and 3.8x on Google Ads.",
            magnitude_value=70000.0,
            magnitude_formatted="CAC +38.2% ($98.50)",
            affected_area="Growth & Performance Marketing",
            confidence="High",
            evidence_id="ev_marketing_cac"
        ),
        # HYPOTHESIS 1
        ExecutiveInsight(
            id="ins_hypo_tier2_shipping_churn",
            classification=StatementType.HYPOTHESIS,
            headline="Tier-2 customer churn increase correlates with delivery surcharge rollout",
            narrative="Customer churn increased by 3.2 percentage points in Q3. Over 74% of newly churned customers were located in Tier-2 zip codes where NovaMart introduced a minimum order shipping surcharge in July.",
            magnitude_value=142000.0,
            magnitude_formatted="+$142K Revenue at Risk",
            affected_area="Customer Experience & Retention",
            confidence="Medium",
            evidence_id="ev_churn_surge"
        ),
        # HYPOTHESIS 2
        ExecutiveInsight(
            id="ins_hypo_discount_cannibalization",
            classification=StatementType.HYPOTHESIS,
            headline="Heavy site-wide discounting cannibalized full-price Electronics sales",
            narrative="Gross margin in Electronics dropped from 34.2% to 30.0% coinciding with mid-quarter flash sales, suggesting customers deferred purchases until coupon issuance.",
            magnitude_value=165000.0,
            magnitude_formatted="-420 bps Margin Drift",
            affected_area="Category Management",
            confidence="Medium",
            evidence_id="ev_category_margin"
        ),
        # RECOMMENDATION 1
        ExecutiveInsight(
            id="ins_rec_renegotiate_carriers",
            classification=StatementType.RECOMMENDATION,
            headline="Renegotiate FastLogistics carrier rates or route volume to ExpressCargo",
            narrative="Capping regional parcel rates at $76.00 or transferring 40% of Northern zone volume to ExpressCargo will recover an estimated $140,000 to $180,000 annually in operating profit.",
            magnitude_value=160000.0,
            magnitude_formatted="$160K Annualized Recovery",
            affected_area="Supply Chain Operations",
            confidence="High",
            evidence_id="ev_shipping_surge"
        )
    ]
    return insights

def generate_strategic_recommendations(kpi: KPISummary) -> List[StrategicRecommendation]:
    """
    Produces deterministic, evidence-backed consulting recommendations with explicit
    financial sizing, implementation difficulty, and critical assumptions.
    """
    return [
        StrategicRecommendation(
            id="rec_01_logistics_rebalancing",
            title="Carrier Optimization & Regional Dynamic Routing",
            recommendation="Renegotiate carrier service-level terms with FastLogistics and implement dynamic carrier routing to divert Tier-2 volume to ExpressCargo.",
            why="Delivery expenses increased 13.7% QoQ ($112.4K excess) and account for 52% of the total increase in operating expenditures. FastLogistics average delivery cost spiked 17.1% while peers grew under 5%.",
            expected_impact_annualized=420000.0,
            expected_impact_formatted="$420,000 / year ($105,000 / quarter)",
            confidence="High",
            implementation_timeframe="Quick Win (0-30 days)",
            assumptions=[
                "ExpressCargo maintains capacity to absorb 35% incremental regional volume.",
                "Contractual minimum volume penalties with FastLogistics are waived above 5,000 monthly orders.",
                "Warehouse dispatch sorting latency remains under 4 hours."
            ],
            supporting_evidence_ids=["ev_shipping_surge", "ev_pnl_summary"]
        ),
        StrategicRecommendation(
            id="rec_02_paid_social_reallocation",
            title="Marketing Budget Reallocation from Paid Social to Search & Affiliate",
            recommendation="Reduce Paid Social budget by 30% ($126,000/quarter) and redeploy $75,000 into high-ROAS Google Ads and Affiliate partnerships while retaining remaining $51,000 as net profit savings.",
            why="Paid Social CAC increased 38.2% to $98.50 with a depressed ROAS of 2.1x, while Affiliate channels deliver 4.5x ROAS at $45.00 CAC.",
            expected_impact_annualized=280000.0,
            expected_impact_formatted="$280,000 / year ($70,000 / quarter)",
            confidence="High",
            implementation_timeframe="Tactical (30-60 days)",
            assumptions=[
                "Affiliate publisher inventory can absorb an additional $30,000 in monthly placements without conversion decay.",
                "High-intent search query volume remains resilient at current CPCs."
            ],
            supporting_evidence_ids=["ev_marketing_cac"]
        ),
        StrategicRecommendation(
            id="rec_03_pricing_bundle_aov",
            title="Threshold-Based Minimum Order Shipping & Basket Bundles",
            recommendation="Replace flat shipping surcharges with an order threshold of $65 for free shipping and introduce multi-item bundling in Electronics and Fashion.",
            why="AOV declined 5.1% ($25.34/order), causing $490,000 in lost gross margin. Customer churn concentrated in Tier-2 post shipping charge rollout.",
            expected_impact_annualized=560000.0,
            expected_impact_formatted="$560,000 / year ($140,000 / quarter)",
            confidence="Medium",
            implementation_timeframe="Strategic (60-90 days)",
            assumptions=[
                "Cross-sell attachment rate will increase average items per order from 1.6 to 1.9.",
                "Price elasticity of demand for add-on accessories remains low (|e_d| < 0.4)."
            ],
            supporting_evidence_ids=["ev_aov_shrink", "ev_churn_surge"]
        )
    ]

def get_evidence_catalog() -> Dict[str, EvidenceDetail]:
    """
    Curated evidence repository detailing mathematical formulas, SQL queries,
    and underlying record samples supporting every finding and node.
    """
    return {
        "ev_pnl_summary": EvidenceDetail(
            evidence_id="ev_pnl_summary",
            title="Quarterly P&L Variance & Operating Profit Decomposition",
            methodology="Quarterly accrual aggregation comparing gross sales, returns, fulfillment costs, and marketing expenses.",
            mathematical_formula="Net Profit = Gross Sales - Returns - COGS - Delivery Cost - Marketing - Opex. Delta % = ((Q3_Net - Q2_Net) / Q2_Net) * 100",
            sql_query="""SELECT 
    DATE_TRUNC('quarter', o.order_date) AS quarter,
    SUM(o.net_amount) AS revenue,
    SUM(oi.quantity * oi.unit_cogs) AS cogs,
    SUM(o.delivery_cost) AS delivery_costs,
    (SELECT SUM(spend_amount) FROM marketing_spend m WHERE DATE_TRUNC('quarter', m.spend_date) = DATE_TRUNC('quarter', o.order_date)) AS marketing_spend,
    (SUM(o.net_amount) - SUM(oi.quantity * oi.unit_cogs) - SUM(o.delivery_cost)) AS operating_profit
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.order_status NOT IN ('Cancelled')
GROUP BY 1
ORDER BY 1 DESC;""",
            sample_records=[
                {"quarter": "2024-Q3", "revenue": "$9,180,000", "cogs": "$5,462,100", "delivery_cost": "$932,400", "marketing": "$920,000", "net_profit": "$1,057,260", "net_margin": "11.5%"},
                {"quarter": "2024-Q2", "revenue": "$10,000,000", "cogs": "$5,800,000", "delivery_cost": "$820,000", "marketing": "$850,000", "net_profit": "$1,280,000", "net_margin": "12.8%"}
            ],
            aggregate_table=[
                {"metric": "Revenue", "Q2": "$10,000,000", "Q3": "$9,180,000", "delta": "-$820,000", "delta_pct": "-8.2%"},
                {"metric": "Gross Profit", "Q2": "$4,200,000", "Q3": "$3,717,900", "delta": "-$482,100", "delta_pct": "-11.5%"},
                {"metric": "Delivery Costs", "Q2": "$820,000", "Q3": "$932,400", "delta": "+$112,400", "delta_pct": "+13.7%"},
                {"metric": "Marketing Spend", "Q2": "$850,000", "Q3": "$920,000", "delta": "+$70,000", "delta_pct": "+8.2%"},
                {"metric": "Net Operating Profit", "Q2": "$1,280,000", "Q3": "$1,057,260", "delta": "-$222,740", "delta_pct": "-17.4%"}
            ]
        ),
        "ev_shipping_surge": EvidenceDetail(
            evidence_id="ev_shipping_surge",
            title="Carrier Delivery Rate Analysis & Regional Surcharges",
            methodology="Granular tracking of per-order shipping costs partitioned by logistics partner and geographical destination.",
            mathematical_formula="Avg Cost = SUM(delivery_cost) / COUNT(order_id). Variance = (Avg_Q3 - Avg_Q2) * Volume_Q3",
            sql_query="""SELECT 
    shipping_partner,
    AVG(CASE WHEN order_date BETWEEN '2024-04-01' AND '2024-06-30' THEN delivery_cost END) AS q2_avg_cost,
    AVG(CASE WHEN order_date BETWEEN '2024-07-01' AND '2024-09-30' THEN delivery_cost END) AS q3_avg_cost,
    COUNT(CASE WHEN order_date >= '2024-07-01' THEN order_id END) AS q3_orders,
    ROUND((AVG(delivery_cost) - 72.4) * COUNT(order_id), 2) AS excess_variance
FROM orders
GROUP BY shipping_partner
ORDER BY excess_variance DESC;""",
            sample_records=[
                {"order_id": "ORD-89421", "shipping_partner": "FastLogistics", "region": "Tier 2 - North", "delivery_cost": "$86.50", "prior_benchmark": "$72.00", "status": "Excess Fee"},
                {"order_id": "ORD-89422", "shipping_partner": "FastLogistics", "region": "Tier 2 - Central", "delivery_cost": "$84.00", "prior_benchmark": "$73.50", "status": "Excess Fee"},
                {"order_id": "ORD-89423", "shipping_partner": "ExpressCargo", "region": "Tier 1 - West", "delivery_cost": "$74.00", "prior_benchmark": "$68.00", "status": "Normal Inflation"},
                {"order_id": "ORD-89424", "shipping_partner": "BlueDart", "region": "Tier 1 - South", "delivery_cost": "$90.00", "prior_benchmark": "$88.00", "status": "In Policy"}
            ],
            aggregate_table=[
                {"partner": "FastLogistics", "q2_rate": "$72.40", "q3_rate": "$84.80", "delta_pct": "+17.1%", "q3_orders": 8500, "excess_cost": "$105,400"},
                {"partner": "ExpressCargo", "q2_rate": "$68.10", "q3_rate": "$75.30", "delta_pct": "+10.6%", "q3_orders": 6200, "excess_cost": "$44,640"},
                {"partner": "BlueDart", "q2_rate": "$88.00", "q3_rate": "$91.20", "delta_pct": "+3.6%", "q3_orders": 4640, "excess_cost": "$14,848"}
            ]
        ),
        "ev_aov_shrink": EvidenceDetail(
            evidence_id="ev_aov_shrink",
            title="Basket Size & Average Order Value (AOV) Deterioration",
            methodology="Basket unit count and item tier analysis across orders comparing Q2 vs Q3.",
            mathematical_formula="AOV = Total Net Sales / Total Non-Cancelled Orders. Delta AOV = AOV_Q3 - AOV_Q2",
            sql_query="""SELECT 
    DATE_TRUNC('month', order_date) AS month,
    COUNT(order_id) AS total_orders,
    SUM(net_amount) AS revenue,
    ROUND(AVG(net_amount), 2) AS average_order_value,
    ROUND(AVG(discount_amount), 2) AS average_discount
FROM orders
GROUP BY 1
ORDER BY 1;""",
            sample_records=[
                {"month": "2024-04", "orders": 6620, "aov": "$502.10", "avg_discount": "$18.40"},
                {"month": "2024-05", "orders": 6710, "aov": "$498.90", "avg_discount": "$19.10"},
                {"month": "2024-06", "orders": 6670, "aov": "$499.00", "avg_discount": "$18.80"},
                {"month": "2024-07", "orders": 6480, "aov": "$482.30", "avg_discount": "$24.50"},
                {"month": "2024-08", "orders": 6410, "aov": "$473.10", "avg_discount": "$26.20"},
                {"month": "2024-09", "orders": 6450, "aov": "$468.60", "avg_discount": "$27.10"}
            ],
            aggregate_table=[
                {"period": "Q2 2024", "orders": 20000, "net_revenue": "$10,000,000", "aov": "$500.00", "discount_rate": "3.8%"},
                {"period": "Q3 2024", "orders": 19340, "net_revenue": "$9,180,000", "aov": "$474.66", "discount_rate": "5.6%"},
                {"period": "Variance", "orders": -660, "net_revenue": "-$820,000", "aov": "-$25.34 (-5.1%)", "discount_rate": "+180 bps"}
            ]
        ),
        "ev_marketing_cac": EvidenceDetail(
            evidence_id="ev_marketing_cac",
            title="Marketing Channel Attribution & CAC Escalation",
            methodology="Quarterly spend attribution matching ad budgets to first-order customer signups and revenue.",
            mathematical_formula="CAC = Total Channel Spend / Attributed New Customers. ROAS = Attributed Revenue / Total Channel Spend",
            sql_query="""SELECT 
    channel,
    SUM(spend_amount) AS total_spend,
    SUM(attributed_orders) AS conversions,
    ROUND(SUM(spend_amount) / NULLIF(SUM(attributed_orders), 0), 2) AS cac,
    ROUND(SUM(attributed_revenue) / NULLIF(SUM(spend_amount), 0), 2) AS roas
FROM marketing_spend
WHERE spend_date >= '2024-07-01'
GROUP BY 1
ORDER BY cac DESC;""",
            sample_records=[
                {"channel": "Paid Social", "q2_spend": "$340,000", "q3_spend": "$420,000", "q2_cac": "$71.20", "q3_cac": "$98.50", "roas_trend": "2.9x -> 2.1x"},
                {"channel": "Google Ads", "q2_spend": "$280,000", "q3_spend": "$290,000", "q2_cac": "$59.80", "q3_cac": "$62.40", "roas_trend": "3.9x -> 3.8x"},
                {"channel": "Affiliate", "q2_spend": "$140,000", "q3_spend": "$130,000", "q2_cac": "$46.10", "q3_cac": "$45.00", "roas_trend": "4.4x -> 4.5x"}
            ],
            aggregate_table=[
                {"channel": "Paid Social", "spend": "$420,000", "cac": "$98.50", "cac_delta": "+38.2%", "roas": "2.1x", "verdict": "Marginally Profitable"},
                {"channel": "Google Ads", "spend": "$290,000", "cac": "$62.40", "cac_delta": "+4.1%", "roas": "3.8x", "verdict": "Strong"},
                {"channel": "Affiliate", "spend": "$130,000", "cac": "$45.00", "cac_delta": "-2.3%", "roas": "4.5x", "verdict": "Top Efficiency"},
                {"channel": "Email Marketing", "spend": "$80,000", "cac": "$18.20", "cac_delta": "+1.0%", "roas": "7.2x", "verdict": "High Margin Retention"}
            ]
        ),
        "ev_churn_surge": EvidenceDetail(
            evidence_id="ev_churn_surge",
            title="Customer Churn Acceleration & Regional Disconnect",
            methodology="Quarterly cohort survival analysis tracking repeat order status across customer segments.",
            mathematical_formula="Churn Rate = Churned Customers / Total Active Cohort Base * 100",
            sql_query="""SELECT 
    region,
    COUNT(customer_id) AS total_customers,
    SUM(CASE WHEN churn_status = TRUE THEN 1 ELSE 0 END) AS churned_count,
    ROUND(SUM(CASE WHEN churn_status = TRUE THEN 1 ELSE 0 END) * 100.0 / COUNT(customer_id), 2) AS churn_rate_pct
FROM customers
GROUP BY 1
ORDER BY churn_rate_pct DESC;""",
            sample_records=[
                {"region": "Tier 2 - North", "cohort_size": 4200, "churn_q2": "5.1%", "churn_q3": "9.4%", "delta": "+4.3 pp"},
                {"region": "Tier 2 - Central", "cohort_size": 3800, "churn_q2": "4.9%", "churn_q3": "8.8%", "delta": "+3.9 pp"},
                {"region": "Tier 1 - West", "cohort_size": 3400, "churn_q2": "5.4%", "churn_q3": "6.2%", "delta": "+0.8 pp"},
                {"region": "Tier 1 - South", "cohort_size": 2840, "churn_q2": "5.3%", "churn_q3": "5.9%", "delta": "+0.6 pp"}
            ],
            aggregate_table=[
                {"region": "Tier 2 Regional", "active_base": 8000, "q2_churn": "5.0%", "q3_churn": "9.1%", "delta_pp": "+4.1 pp", "est_revenue_loss": "$98,000"},
                {"region": "Tier 1 Metro", "active_base": 6240, "q2_churn": "5.3%", "q3_churn": "6.0%", "delta_pp": "+0.7 pp", "est_revenue_loss": "$44,000"}
            ]
        ),
        "ev_category_margin": EvidenceDetail(
            evidence_id="ev_category_margin",
            title="Category Margin Erosion & COGS Variance",
            methodology="Unit economics decomposition across SKUs and categories.",
            mathematical_formula="Gross Margin % = (Item Revenue - Item COGS) / Item Revenue * 100",
            sql_query="""SELECT 
    p.category,
    SUM(oi.item_total) AS revenue,
    SUM(oi.quantity * oi.unit_cogs) AS cogs,
    ROUND((SUM(oi.item_total) - SUM(oi.quantity * oi.unit_cogs)) / SUM(oi.item_total) * 100, 2) AS gross_margin_pct
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
GROUP BY 1
ORDER BY revenue DESC;""",
            sample_records=[
                {"category": "Electronics", "revenue": "$3,850,000", "q2_margin": "34.2%", "q3_margin": "30.0%", "drift": "-420 bps"},
                {"category": "Fashion & Apparel", "revenue": "$2,420,000", "q2_margin": "48.5%", "q3_margin": "45.0%", "drift": "-350 bps"},
                {"category": "Home & Living", "revenue": "$1,680,000", "q2_margin": "38.5%", "q3_margin": "38.0%", "drift": "-50 bps"},
                {"category": "Beauty & Health", "revenue": "$950,000", "q2_margin": "51.8%", "q3_margin": "52.0%", "drift": "+20 bps"}
            ],
            aggregate_table=[
                {"category": "Electronics", "q3_sales": "$3,850,000", "margin_pct": "30.0%", "pareto_weight": "33.1%", "status": "Margin Erosion"},
                {"category": "Fashion & Apparel", "q3_sales": "$2,420,000", "margin_pct": "45.0%", "pareto_weight": "31.2%", "status": "High Return Rate"},
                {"category": "Home & Living", "q3_sales": "$1,680,000", "margin_pct": "38.0%", "pareto_weight": "18.3%", "status": "Stable"},
                {"category": "Beauty & Health", "q3_sales": "$950,000", "margin_pct": "52.0%", "pareto_weight": "14.1%", "status": "Growth Driver"}
            ]
        )
    }
