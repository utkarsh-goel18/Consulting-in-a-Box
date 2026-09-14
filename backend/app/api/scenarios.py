from fastapi import APIRouter
from app.core.database import repo
from app.engine.analytics_engine import DeterministicAnalyticsEngine
from app.engine.scenario_simulator import run_what_if_simulation
from app.models.schemas import ScenarioLevers, ScenarioResult

router = APIRouter(prefix="/scenarios", tags=["scenarios"])


@router.post("/simulate", response_model=ScenarioResult)
def simulate_scenario(levers: ScenarioLevers):
    """Execute a deterministic what-if simulation against the current verified base case."""
    engine = DeterministicAnalyticsEngine(repo.dataframes)
    snapshot = engine.analysis_snapshot()
    costs = engine._period_costs()
    snapshot["costs"] = {"marketing_delta": costs["Marketing Spend"][1] - costs["Marketing Spend"][0]}
    snapshot["delivery_current"] = costs["Delivery Costs"][1]
    return run_what_if_simulation(snapshot["kpi"], levers, snapshot)
