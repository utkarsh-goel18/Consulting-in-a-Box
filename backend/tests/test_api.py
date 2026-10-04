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


def test_pdf_download():
    with TestClient(app) as c:
        response = c.get("/api/reports/download-pdf")
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"
        assert len(response.content) > 1000


def test_settings_endpoints():
    with TestClient(app) as c:
        res = c.get("/api/settings")
        assert res.status_code == 200
        data = res.json()
        assert "demo_mode" in data
        assert "ai_provider" in data

        update_res = c.post("/api/settings", json={"demo_mode": True, "ai_provider": "mock"})
        assert update_res.status_code == 200
        assert update_res.json()["status"] == "success"


def test_table_preview():
    with TestClient(app) as c:
        res = c.get("/api/datasets/orders/preview")
        assert res.status_code == 200
        data = res.json()
        assert data["dataset_name"] == "orders"
        assert len(data["records"]) > 0


def test_ai_provider():
    from app.ai.openai_provider import OpenAIProvider
    from app.ai.gemini_provider import GeminiAIProvider
    from app.ai.mock_consultant import MockStrategicConsultant

    mock_p = MockStrategicConsultant()
    plan = mock_p.generate_analysis_plan("Profit drop diagnostic", {"case_id": "case_profitability_decline"})
    assert len(plan.steps) > 0

    openai_p = OpenAIProvider(api_key=None)
    plan_o = openai_p.generate_analysis_plan("Profit drop diagnostic", {"case_id": "case_profitability_decline"})
    assert len(plan_o.steps) > 0

    gemini_p = GeminiAIProvider(api_key=None)
    plan_g = gemini_p.generate_analysis_plan("Profit drop diagnostic", {"case_id": "case_profitability_decline"})
    assert len(plan_g.steps) > 0