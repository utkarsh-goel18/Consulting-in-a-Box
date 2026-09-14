import pandas as pd
from app.engine.profiler import profile_dataframe, detect_relationships
from app.engine.analytics_engine import DeterministicAnalyticsEngine
from app.engine.driver_tree import build_driver_tree
from app.engine.scenario_simulator import run_what_if_simulation
from app.reports.pdf_generator import generate_consulting_pdf
from app.models.schemas import ScenarioLevers, KPISummary


def sample_kpi():
    return KPISummary(
        revenue_prior=10_000_000, revenue_current=9_180_000, revenue_growth_pct=-8.2,
        gross_profit_prior=4_200_000, gross_profit_current=3_717_900, gross_profit_growth_pct=-11.5,
        net_profit_prior=1_280_000, net_profit_current=1_057_260, net_profit_growth_pct=-17.4,
        net_margin_prior_pct=12.8, net_margin_current_pct=11.5, net_margin_delta_pp=-1.3,
        orders_prior=20_000, orders_current=19_340, orders_growth_pct=-3.3,
        aov_prior=500, aov_current=474.66, aov_growth_pct=-5.1,
        active_customers_prior=14_500, active_customers_current=14_240, active_customers_growth_pct=-1.8,
        cac_prior=58.62, cac_current=64.61, cac_growth_pct=10.2,
        churn_rate_prior_pct=5.2, churn_rate_current_pct=8.4, churn_rate_delta_pp=3.2,
    )


def test_profiler():
    df = pd.DataFrame({"customer_id": ["C1", "C2", "C3", "C4"], "region": ["North", "South", "North", "West"], "spend": [100.5, 250.0, 75.25, 420.0]})
    profile = profile_dataframe("test_cust", "test_cust.csv", df)
    assert profile.row_count == 4
    assert profile.column_count == 3
    assert "customer_id" in profile.likely_primary_keys
    assert profile.data_quality_score >= 80.0


def test_driver_tree_reconciles():
    tree = build_driver_tree(sample_kpi())
    assert tree.metric_name == "Net Profit"
    assert round(tree.delta_pct, 1) == -17.4
    assert len(tree.children) >= 2
    assert abs(sum(child.delta_value for child in tree.children) - tree.delta_value) < 1e-6
    revenue = next(c for c in tree.children if c.id == "drv_revenue")
    assert len(revenue.children) >= 2


def test_scenario_simulator():
    result = run_what_if_simulation(sample_kpi(), ScenarioLevers(price_change_pct=5, delivery_cost_delta_pct=-8))
    assert "Net Profit" in result.metrics
    assert result.metrics["Net Profit"].scenario_value > result.metrics["Net Profit"].base_value
    assert len(result.waterfall_breakdown) > 0
    assert len(result.key_assumptions) > 0


def test_pdf_report_generation():
    kpi = sample_kpi()
    payload = {"company_name": "NovaMart", "industry": "E-commerce", "quarter_evaluated": "Q3 2024 vs Q2 2024", "problem_title": "Profitability Decline", "kpi_summary": kpi.model_dump(), "insights": [], "recommendations": []}
    pdf_bytes = generate_consulting_pdf(payload)
    assert len(pdf_bytes) > 1000
    assert pdf_bytes.startswith(b"%PDF")
