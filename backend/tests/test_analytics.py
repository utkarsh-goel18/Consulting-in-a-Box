import os
import pytest
import pandas as pd
from app.engine.profiler import profile_dataframe, detect_relationships
from app.engine.analytics_engine import DeterministicAnalyticsEngine
from app.engine.driver_tree import build_driver_tree
from app.engine.scenario_simulator import run_what_if_simulation
from app.reports.pdf_generator import generate_consulting_pdf
from app.models.schemas import ScenarioLevers, KPISummary

def test_profiler():
    df = pd.DataFrame({
        "customer_id": ["C1", "C2", "C3", "C4"],
        "region": ["North", "South", "North", "West"],
        "spend": [100.5, 250.0, 75.25, 420.0]
    })
    profile = profile_dataframe("test_cust", "test_cust.csv", df)
    assert profile.row_count == 4
    assert profile.column_count == 3
    assert "customer_id" in profile.likely_primary_keys
    assert profile.data_quality_score >= 80.0

def test_driver_tree_decomposition():
    kpi = KPISummary(
        revenue_prior=10000000.0,
        revenue_current=9180000.0,
        revenue_growth_pct=-8.2,
        gross_profit_prior=4200000.0,
        gross_profit_current=3717900.0,
        gross_profit_growth_pct=-11.5,
        net_profit_prior=1280000.0,
        net_profit_current=1057260.0,
        net_profit_growth_pct=-17.4,
        net_margin_prior_pct=12.8,
        net_margin_current_pct=11.5,
        net_margin_delta_pp=-1.3,
        orders_prior=20000,
        orders_current=19340,
        orders_growth_pct=-3.3,
        aov_prior=500.0,
        aov_current=474.66,
        aov_growth_pct=-5.1,
        active_customers_prior=14500,
        active_customers_current=14240,
        active_customers_growth_pct=-1.8,
        cac_prior=58.62,
        cac_current=64.61,
        cac_growth_pct=10.2,
        churn_rate_prior_pct=5.2,
        churn_rate_current_pct=8.4,
        churn_rate_delta_pp=3.2
    )
    
    tree = build_driver_tree(kpi)
    assert tree.metric_name == "Net Profit"
    assert tree.delta_pct == -17.4
    assert len(tree.children) == 2 # Revenue and Costs branches
    
    rev_node = next(c for c in tree.children if c.id == "driver_revenue")
    cost_node = next(c for c in tree.children if c.id == "driver_costs")
    
    assert rev_node.delta_pct == -8.2
    assert cost_node.delta_pct == 11.7
    assert len(rev_node.children) >= 2 # AOV and Orders
    assert len(cost_node.children) >= 3 # Delivery, Marketing, Returns

def test_scenario_simulator():
    kpi = KPISummary(
        revenue_prior=10000000.0,
        revenue_current=9180000.0,
        revenue_growth_pct=-8.2,
        gross_profit_prior=4200000.0,
        gross_profit_current=3717900.0,
        gross_profit_growth_pct=-11.5,
        net_profit_prior=1280000.0,
        net_profit_current=1057260.0,
        net_profit_growth_pct=-17.4,
        net_margin_prior_pct=12.8,
        net_margin_current_pct=11.5,
        net_margin_delta_pp=-1.3,
        orders_prior=20000,
        orders_current=19340,
        orders_growth_pct=-3.3,
        aov_prior=500.0,
        aov_current=474.66,
        aov_growth_pct=-5.1,
        active_customers_prior=14500,
        active_customers_current=14240,
        active_customers_growth_pct=-1.8,
        cac_prior=58.62,
        cac_current=64.61,
        cac_growth_pct=10.2,
        churn_rate_prior_pct=5.2,
        churn_rate_current_pct=8.4,
        churn_rate_delta_pp=3.2
    )
    
    # Simulate a 5% price increase and 8% delivery cost reduction
    levers = ScenarioLevers(price_change_pct=5.0, delivery_cost_delta_pct=-8.0)
    result = run_what_if_simulation(kpi, levers)
    
    assert "Net Profit" in result.metrics
    # Net profit should improve with price increase and cost reduction
    assert result.metrics["Net Profit"].scenario_value > result.metrics["Net Profit"].base_value
    assert len(result.waterfall_breakdown) > 0
    assert len(result.key_assumptions) > 0

def test_pdf_report_generation():
    kpi = KPISummary(
        revenue_prior=10000000.0,
        revenue_current=9180000.0,
        revenue_growth_pct=-8.2,
        gross_profit_prior=4200000.0,
        gross_profit_current=3717900.0,
        gross_profit_growth_pct=-11.5,
        net_profit_prior=1280000.0,
        net_profit_current=1057260.0,
        net_profit_growth_pct=-17.4,
        net_margin_prior_pct=12.8,
        net_margin_current_pct=11.5,
        net_margin_delta_pp=-1.3,
        orders_prior=20000,
        orders_current=19340,
        orders_growth_pct=-3.3,
        aov_prior=500.0,
        aov_current=474.66,
        aov_growth_pct=-5.1,
        active_customers_prior=14500,
        active_customers_current=14240,
        active_customers_growth_pct=-1.8,
        cac_prior=58.62,
        cac_current=64.61,
        cac_growth_pct=10.2,
        churn_rate_prior_pct=5.2,
        churn_rate_current_pct=8.4,
        churn_rate_delta_pp=3.2
    )
    
    payload = {
        "company_name": "NovaMart",
        "industry": "E-commerce",
        "quarter_evaluated": "Q3 2024 vs Q2 2024",
        "problem_title": "Profitability Decline",
        "kpi_summary": kpi.dict(),
        "insights": [],
        "recommendations": []
    }
    
    pdf_bytes = generate_consulting_pdf(payload)
    assert len(pdf_bytes) > 1000
    assert pdf_bytes.startswith(b"%PDF")
