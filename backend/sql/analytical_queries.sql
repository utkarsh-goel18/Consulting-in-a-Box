-- ============================================================================
-- Consulting in a Box - Curated Strategic Analytical SQL Queries
-- Reusable Enterprise Decision-Intelligence & Root Cause Queries
-- ============================================================================

-- 1. EXECUTIVE P&L STATEMENT BY QUARTER (Variance & Margin Analysis)
WITH quarterly_revenue AS (
    SELECT 
        DATE_TRUNC('quarter', o.order_date) AS quarter,
        COUNT(DISTINCT o.order_id) AS total_orders,
        COUNT(DISTINCT o.customer_id) AS active_customers,
        SUM(o.net_amount) AS total_net_revenue,
        AVG(o.net_amount) AS average_order_value,
        SUM(o.delivery_cost) AS total_delivery_cost
    FROM orders o
    WHERE o.order_status NOT IN ('Cancelled')
    GROUP BY 1
),
quarterly_cogs AS (
    SELECT 
        DATE_TRUNC('quarter', o.order_date) AS quarter,
        SUM(oi.quantity * oi.unit_cogs) AS total_cogs
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.order_status NOT IN ('Cancelled')
    GROUP BY 1
),
quarterly_marketing AS (
    SELECT 
        DATE_TRUNC('quarter', spend_date) AS quarter,
        SUM(spend_amount) AS total_marketing_spend
    FROM marketing_spend
    GROUP BY 1
),
quarterly_expenses AS (
    SELECT 
        DATE_TRUNC('quarter', expense_date) AS quarter,
        SUM(amount) AS total_operating_expenses
    FROM expenses
    GROUP BY 1
),
quarterly_returns AS (
    SELECT 
        DATE_TRUNC('quarter', return_date) AS quarter,
        SUM(refund_amount) AS total_refunds,
        SUM(reverse_logistics_cost) AS total_return_logistics
    FROM returns
    GROUP BY 1
)
SELECT 
    r.quarter,
    r.total_orders,
    r.active_customers,
    r.total_net_revenue,
    r.average_order_value,
    c.total_cogs,
    (r.total_net_revenue - c.total_cogs) AS gross_profit,
    ROUND(((r.total_net_revenue - c.total_cogs) / NULLIF(r.total_net_revenue, 0) * 100), 2) AS gross_margin_pct,
    r.total_delivery_cost,
    m.total_marketing_spend,
    e.total_operating_expenses,
    (ret.total_refunds + ret.total_return_logistics) AS total_return_costs,
    -- Net Operating Profit
    (r.total_net_revenue - c.total_cogs - r.total_delivery_cost - m.total_marketing_spend - e.total_operating_expenses - ret.total_return_logistics) AS net_profit,
    ROUND(((r.total_net_revenue - c.total_cogs - r.total_delivery_cost - m.total_marketing_spend - e.total_operating_expenses - ret.total_return_logistics) / NULLIF(r.total_net_revenue, 0) * 100), 2) AS net_margin_pct
FROM quarterly_revenue r
LEFT JOIN quarterly_cogs c ON r.quarter = c.quarter
LEFT JOIN quarterly_marketing m ON r.quarter = m.quarter
LEFT JOIN quarterly_expenses e ON r.quarter = e.quarter
LEFT JOIN quarterly_returns ret ON r.quarter = ret.quarter
ORDER BY r.quarter DESC;


-- 2. ROOT CAUSE: DELIVERY COST VARIANCE BY SHIPPING PARTNER & ROUTE
SELECT 
    o.shipping_partner,
    DATE_TRUNC('quarter', o.order_date) AS quarter,
    COUNT(o.order_id) AS orders_handled,
    SUM(o.delivery_cost) AS total_delivery_cost,
    AVG(o.delivery_cost) AS avg_delivery_cost_per_order,
    LAG(AVG(o.delivery_cost)) OVER (PARTITION BY o.shipping_partner ORDER BY DATE_TRUNC('quarter', o.order_date)) AS prior_avg_delivery_cost,
    ROUND(
        (AVG(o.delivery_cost) - LAG(AVG(o.delivery_cost)) OVER (PARTITION BY o.shipping_partner ORDER BY DATE_TRUNC('quarter', o.order_date))) 
        / NULLIF(LAG(AVG(o.delivery_cost)) OVER (PARTITION BY o.shipping_partner ORDER BY DATE_TRUNC('quarter', o.order_date)), 0) * 100, 2
    ) AS cost_increase_pct
FROM orders o
GROUP BY 1, 2
ORDER BY shipping_partner, quarter;


-- 3. PRODUCT CATEGORY MARGIN & PARETO CONTRIBUTION
SELECT 
    p.category,
    COUNT(DISTINCT oi.order_id) AS orders_count,
    SUM(oi.quantity) AS units_sold,
    SUM(oi.item_total) AS total_sales,
    SUM(oi.gross_margin) AS total_gross_margin,
    ROUND((SUM(oi.gross_margin) / NULLIF(SUM(oi.item_total), 0) * 100), 2) AS category_margin_pct,
    ROUND(
        SUM(oi.gross_margin) / SUM(SUM(oi.gross_margin)) OVER () * 100, 2
    ) AS contribution_to_total_margin_pct
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
GROUP BY 1
ORDER BY total_gross_margin DESC;


-- 4. MARKETING CHANNEL EFFICIENCY & CAC ANALYSIS
SELECT 
    m.channel,
    DATE_TRUNC('quarter', m.spend_date) AS quarter,
    SUM(m.spend_amount) AS total_spend,
    SUM(m.attributed_orders) AS attributed_orders,
    SUM(m.attributed_revenue) AS attributed_revenue,
    ROUND(SUM(m.spend_amount) / NULLIF(SUM(m.attributed_orders), 0), 2) AS cost_per_acquisition_cac,
    ROUND(SUM(m.attributed_revenue) / NULLIF(SUM(m.spend_amount), 0), 2) AS roas_multiplier
FROM marketing_spend m
GROUP BY 1, 2
ORDER BY quarter DESC, cost_per_acquisition_cac DESC;


-- 5. COHORT RETENTION & CHURN BY SIGNUP QUARTER
SELECT 
    DATE_TRUNC('quarter', signup_date) AS cohort_quarter,
    COUNT(customer_id) AS cohort_size,
    COUNT(CASE WHEN churn_status = TRUE THEN 1 END) AS churned_customers,
    ROUND(COUNT(CASE WHEN churn_status = TRUE THEN 1 END) * 100.0 / COUNT(customer_id), 2) AS churn_rate_pct,
    COUNT(CASE WHEN region = 'North' AND churn_status = TRUE THEN 1 END) AS churn_north,
    COUNT(CASE WHEN region = 'Tier 2' AND churn_status = TRUE THEN 1 END) AS churn_tier2
FROM customers
GROUP BY 1
ORDER BY cohort_quarter;
