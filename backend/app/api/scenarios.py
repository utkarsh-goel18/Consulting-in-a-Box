from fastapi import APIRouter
from app.core.database import repo
from app.engine.analytics_engine import DeterministicAnalyticsEngine
from app.engine.scenario_simulator import run_what_if_simulation
from app.models.schemas import ScenarioLevers, ScenarioResult

router = APIRouter(prefix="/scenarios", tags=["scenarios"])

@router.post("/simulate", response_model=ScenarioResult)
def simulate_scenario(levers: ScenarioLevers):
    """
    Executes what-if financial simulation across pricing, marketing, churn,
    delivery costs, and COGS levers, computing exact variance against base case.
    """
    engine = DeterministicAnalyticsEngine(repo.dataframes)
    kpi = engine.calculate_executive_kpis()
    return run_what_if_simulation(kpi, levers)
