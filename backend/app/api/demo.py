import os
import pandas as pd
from fastapi import APIRouter
from app.core.config import settings
from app.core.database import repo
from app.engine.demo_data import generate_datasets
from app.engine.analytics_engine import DeterministicAnalyticsEngine
from app.engine.driver_tree import build_driver_tree
from app.engine.recommendation_engine import generate_classified_insights, generate_strategic_recommendations
from app.models.schemas import ConsultingDashboard

router = APIRouter(prefix="/demo", tags=["demo"])

# The demo data is deterministic, so there is no reason to recompute the
# complete analytical pipeline every time the frontend refreshes or navigates.
_cached_dashboard: ConsultingDashboard | None = None

@router.post("/bootstrap", response_model=ConsultingDashboard)
def bootstrap_demo():
    """Load the NovaMart demo and return its cached analytical dashboard."""
    global _cached_dashboard
    if _cached_dashboard is not None:
        return _cached_dashboard

    data_dir = settings.DATA_DIR
    required_files = ["customers.csv", "orders.csv", "products.csv", "marketing_spend.csv", "expenses.csv", "returns.csv"]
    all_exist = all(os.path.exists(os.path.join(data_dir, f)) for f in required_files)

    if not all_exist:
        generate_datasets(data_dir, scale="demo")

    # The API lifespan already loads the data into memory. Only fall back to
    # disk loading when this endpoint is used without the normal application startup.
    if not repo.dataframes:
        repo.load_from_directory(data_dir)

    engine = DeterministicAnalyticsEngine(repo.dataframes)
    kpi = engine.calculate_executive_kpis()
    driver_tree = build_driver_tree(kpi)
    insights = generate_classified_insights(kpi)
    recommendations = generate_strategic_recommendations(kpi)
    waterfall = engine.calculate_pnl_waterfall()
    shipping = engine.analyze_shipping_partners()
    categories = engine.analyze_category_margins()
    marketing = engine.analyze_marketing_efficiency()

    orders = repo.dataframes.get("orders", pd.DataFrame())
    monthly_trend = []
    if not orders.empty and "month" in orders.columns:
        m_grouped = orders.groupby("month").agg({"net_amount": "sum", "order_id": "count"}).reset_index()
        monthly_trend = [
            {
                "month": str(row["month"]),
                "revenue": round(float(row["net_amount"]), 2),
                "orders": int(row["order_id"]),
            }
            for _, row in m_grouped.iterrows()
        ]

    _cached_dashboard = ConsultingDashboard(
        company_name="NovaMart",
        industry="E-commerce",
        quarter_evaluated="Q3 2024 vs Q2 2024",
        problem_title="Profitability Decline",
        kpi_summary=kpi,
        driver_tree=driver_tree,
        insights=insights,
        recommendations=recommendations,
        p_and_l_waterfall=waterfall,
        monthly_trend=monthly_trend,
        category_performance=categories,
        marketing_efficiency=marketing,
        shipping_partner_breakdown=shipping,
    )
    return _cached_dashboard
