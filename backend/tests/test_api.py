from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    with TestClient(app) as c:
        response = c.get("/api/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


def test_bootstrap_demo():
    with TestClient(app) as c:
        response = c.post("/api/demo/bootstrap")
        assert response.status_code == 200
        data = response.json()
        assert data["company_name"] == "NovaMart"
        assert len(data["insights"]) > 0
        assert len(data["recommendations"]) > 0
        assert data["kpi_summary"]["currency_symbol"] == "₹"


def test_datasets_overview():
    with TestClient(app) as c:
        response = c.get("/api/datasets/overview")
        assert response.status_code == 200
        data = response.json()
        assert len(data["datasets"]) >= 6
        assert data["overall_quality_score"] > 0


def test_analysis_execute():
    with TestClient(app) as c:
        response = c.post("/api/analysis/execute", json={"case_id": "case_profitability_decline"})
        assert response.status_code == 200
        data = response.json()
        assert len(data["timeline"]) == 5
        assert len(data["result"]["insights"]) > 0


def test_scenario_and_sensitivity():
    payload = {"price_change_pct": 5.0, "marketing_spend_delta_pct": -10.0, "churn_rate_delta_pp": -2.0, "delivery_cost_delta_pct": -8.0, "cogs_reduction_pct": 3.0, "return_rate_delta_pp": -1.0}
    with TestClient(app) as c:
        response = c.post("/api/scenarios/simulate", json=payload)
        assert response.status_code == 200
        assert "Net Profit" in response.json()["metrics"]
        matrix = c.post("/api/scenarios/sensitivity", json=payload)
        assert matrix.status_code == 200
        assert len(matrix.json()["cells"]) == 4


def test_evidence_and_report():
    with TestClient(app) as c:
        evidence = c.get("/api/insights/evidence/ev_shipping_surge")
        assert evidence.status_code == 200
        assert "sql_query" in evidence.json()
        report = c.get("/api/reports/content")
        assert report.status_code == 200
        assert report.json()["currency_symbol"] == "₹"
