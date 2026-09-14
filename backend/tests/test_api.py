from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"

def test_bootstrap_demo():
    response = client.post("/api/demo/bootstrap")
    assert response.status_code == 200
    data = response.json()
    assert data["company_name"] == "NovaMart"
    assert "kpi_summary" in data
    assert "driver_tree" in data
    assert len(data["insights"]) > 0
    assert len(data["recommendations"]) > 0

def test_datasets_overview():
    response = client.get("/api/datasets/overview")
    assert response.status_code == 200
    data = response.json()
    assert len(data["datasets"]) > 0
    assert data["overall_quality_score"] > 0

def test_scenario_simulate():
    payload = {
        "price_change_pct": 5.0,
        "marketing_spend_delta_pct": -10.0,
        "churn_rate_delta_pp": -2.0,
        "delivery_cost_delta_pct": -8.0,
        "cogs_reduction_pct": -3.0,
        "return_rate_delta_pp": -1.0
    }
    response = client.post("/api/scenarios/simulate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "metrics" in data
    assert "Net Profit" in data["metrics"]

def test_evidence_detail():
    response = client.get("/api/insights/evidence/ev_shipping_surge")
    assert response.status_code == 200
    data = response.json()
    assert "mathematical_formula" in data
    assert "sql_query" in data
