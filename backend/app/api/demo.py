import os
import pandas as pd
from fastapi import APIRouter
from app.core.config import settings
from app.core.database import repo
from app.engine.fast_demo_data import generate_fast_demo_datasets, DEMO_VERSION
from app.engine.analytics_engine import DeterministicAnalyticsEngine
from app.engine.driver_tree import build_driver_tree
from app.engine.recommendation_engine import generate_classified_insights, generate_strategic_recommendations
from app.models.schemas import ConsultingDashboard

router = APIRouter(prefix="/demo", tags=["demo"])
_cached_dashboard: ConsultingDashboard | None = None


@router.post("/bootstrap", response_model=ConsultingDashboard)
def bootstrap_demo():
    """Load the NovaMart analytical snapshot and cache it for the process lifetime."""
    global _cached_dashboard
    if _cached_dashboard is not None:
        return _cached_dashboard

    data_dir = settings.DATA_DIR
    required = ["customers.csv", "orders.csv", "products.csv", "order_items.csv", "marketing_spend.csv", "expenses.csv", "returns.csv"]
    version_file = os.path.join(data_dir, ".novamart_demo_version")
    version_ok = os.path.exists(version_file) and open(version_file, encoding="utf-8").read().strip() == DEMO_VERSION
    if not version_ok or any(not os.path.exists(os.path.join(data_dir, name)) for name in required):
        generate_fast_demo_datasets(data_dir)
        repo.dataframes.clear()

    if not repo.dataframes:
        repo.load_from_directory(data_dir)

    engine = DeterministicAnalyticsEngine(repo.dataframes)
    snapshot = engine.analysis_snapshot()
    costs = engine._period_costs()
    snapshot["costs"] = {"marketing_delta": costs["Marketing Spend"][1] - costs["Marketing Spend"][0]}
    snapshot["delivery_current"] = costs["Delivery Costs"][1]
    kpi = snapshot["kpi"]

    driver_tree = build_driver_tree(kpi, snapshot)
    insights = generate_classified_insights(kpi, snapshot)
    recommendations = generate_strategic_recommendations(kpi, snapshot)
    waterfall = snapshot["waterfall"]

    orders = repo.dataframes.get("orders", pd.DataFrame())
    monthly_trend = []
    if not orders.empty and "month" in orders.columns:
        grouped = orders.groupby("month").agg(revenue=("net_amount", "sum"), orders=("order_id", "count")).reset_index()
        monthly_trend = [{"month": str(row.month), "revenue": round(float(row.revenue), 2), "orders": int(row.orders)} for row in grouped.itertuples()]

    q_prior, q_curr = engine._quarters()
    _cached_dashboard = ConsultingDashboard(
        company_name="NovaMart", industry="E-commerce", quarter_evaluated=f"{q_curr} vs {q_prior}", problem_title="Profitability & Growth Performance",
        kpi_summary=kpi, driver_tree=driver_tree, insights=insights, recommendations=recommendations,
        p_and_l_waterfall=waterfall, monthly_trend=monthly_trend,
        category_performance=snapshot["categories"], marketing_efficiency=snapshot["marketing"], shipping_partner_breakdown=snapshot["shipping"],
    )
    return _cached_dashboard
