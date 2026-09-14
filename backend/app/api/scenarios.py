from fastapi import APIRouter

from app.core.analysis_service import get_snapshot
from app.engine.scenario_simulator import run_what_if_simulation
from app.models.schemas import ScenarioLevers, ScenarioResult

router = APIRouter(prefix="/scenarios", tags=["scenarios"])


def _simulate(levers: ScenarioLevers) -> ScenarioResult:
    snapshot = get_snapshot()
    return run_what_if_simulation(snapshot["kpi"], levers, snapshot)


@router.post("/simulate", response_model=ScenarioResult)
def simulate_scenario(levers: ScenarioLevers):
    """Execute a deterministic what-if simulation against the cached verified base case."""
    return _simulate(levers)


@router.post("/sensitivity")
def sensitivity_matrix(levers: ScenarioLevers | None = None):
    """Return a compact price × delivery-cost sensitivity matrix for decision review."""
    base = levers or ScenarioLevers()
    price_values = [-5, 0, 5, 10]
    delivery_values = [-15, -8, 0, 8]
    cells = []
    for price in price_values:
        row = []
        for delivery in delivery_values:
            candidate = base.model_copy(update={"price_change_pct": price, "delivery_cost_delta_pct": delivery})
            result = _simulate(candidate)
            metric = result.metrics["Net Profit"]
            row.append({"price_change_pct": price, "delivery_cost_delta_pct": delivery, "net_profit": metric.scenario_value, "delta_pct": metric.percentage_delta, "favorable": metric.is_positive_trend})
        cells.append(row)
    return {"price_values": price_values, "delivery_cost_values": delivery_values, "cells": cells}
