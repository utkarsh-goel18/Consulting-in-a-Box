import os
import json
import httpx
from typing import Dict, Any, List
from app.ai.base import BaseAIProvider
from app.ai.mock_consultant import MockStrategicConsultant
from app.models.schemas import (
    AnalysisPlan, AnalysisStep, ExecutiveInsight, StatementType, KPISummary
)
from app.core.config import settings


class OpenAIProvider(BaseAIProvider):
    """
    OpenAI Provider for generating structured analysis plans and executive narrative synthesis.
    Works with GPT-4o / GPT-4o-mini / etc.
    """
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or settings.OPENAI_API_KEY or os.getenv("OPENAI_API_KEY")
        self.model = model or "gpt-4o-mini"
        self.fallback = MockStrategicConsultant()

    def generate_analysis_plan(self, business_problem: str, dataset_overview: Dict[str, Any]) -> AnalysisPlan:
        if not self.api_key:
            return self.fallback.generate_analysis_plan(business_problem, dataset_overview)

        system_prompt = "You are a Senior Partner at a premier management consulting firm (McKinsey/BCG). Generate rigorous, quantitative analytical plans."
        user_prompt = f"""A client has presented this business problem: "{business_problem}"
Datasets available: {list(dataset_overview.keys()) if isinstance(dataset_overview, dict) else 'standard tables'}.

Generate an analytical plan decomposed into 4-6 deterministic quantitative steps.
Respond ONLY with a valid JSON object matching this schema:
{{
  "case_id": "case_custom",
  "case_title": "Executive Diagnostic Title",
  "business_question": "{business_problem}",
  "estimated_impact_area": "Primary financial area impacted",
  "steps": [
    {{
      "step_number": 1,
      "title": "Step Title",
      "method": "Analytical Method (e.g. SQL / Variance / Pareto)",
      "description": "Exact quantitative steps to compute",
      "target_metrics": ["Metric 1", "Metric 2"]
    }}
  ]
}}
"""
        try:
            url = "https://api.openai.com/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "response_format": {"type": "json_object"},
                "temperature": 0.2
            }
            with httpx.Client(timeout=12.0) as client:
                res = client.post(url, headers=headers, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    content = data["choices"][0]["message"]["content"]
                    parsed = json.loads(content)
                    steps = [AnalysisStep(**s) for s in parsed.get("steps", [])]
                    return AnalysisPlan(
                        case_id=parsed.get("case_id", "case_custom"),
                        case_title=parsed.get("case_title", "Business Diagnostic"),
                        business_question=business_problem,
                        estimated_impact_area=parsed.get("estimated_impact_area", "Profitability"),
                        steps=steps
                    )
        except Exception:
            pass
        return self.fallback.generate_analysis_plan(business_problem, dataset_overview)

    def synthesize_executive_narrative(
        self, problem_title: str, kpi: KPISummary, root_cause_summary: str
    ) -> str:
        if not self.api_key:
            return self.fallback.synthesize_executive_narrative(problem_title, kpi, root_cause_summary)

        system_prompt = "You are a McKinsey Senior Engagement Partner briefing a Fortune 500 CEO. Keep diagnoses crisp, quantitative, and factual."
        user_prompt = f"""Problem: {problem_title}
Verified Facts:
- Revenue prior: {kpi.revenue_prior:,.2f}, current: {kpi.revenue_current:,.2f} ({kpi.revenue_growth_pct}%)
- Net Profit prior: {kpi.net_profit_prior:,.2f}, current: {kpi.net_profit_current:,.2f} ({kpi.net_profit_growth_pct}%)
- Net Margin: {kpi.net_margin_prior_pct}% to {kpi.net_margin_current_pct}% ({kpi.net_margin_delta_pp} pp)
- Context: {root_cause_summary}

Write a concise, high-impact 3-4 sentence Executive Diagnosis.
Do NOT hallucinate numbers. Use only the figures above.
"""
        try:
            url = "https://api.openai.com/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": 0.3
            }
            with httpx.Client(timeout=12.0) as client:
                res = client.post(url, headers=headers, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    return data["choices"][0]["message"]["content"].strip()
        except Exception:
            pass
        return self.fallback.synthesize_executive_narrative(problem_title, kpi, root_cause_summary)

    def formulate_hypotheses(
        self, anomalies: List[Dict[str, Any]], context: Dict[str, Any]
    ) -> List[ExecutiveInsight]:
        return self.fallback.formulate_hypotheses(anomalies, context)
