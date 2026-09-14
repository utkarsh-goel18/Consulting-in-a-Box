from abc import ABC, abstractmethod
from typing import Dict, Any, List
from app.models.schemas import AnalysisPlan, ExecutiveInsight, StrategicRecommendation, KPISummary

class BaseAIProvider(ABC):
    @abstractmethod
    def generate_analysis_plan(self, business_problem: str, dataset_overview: Dict[str, Any]) -> AnalysisPlan:
        """Generates a structured, multi-step analytical plan based on the problem definition."""
        pass
        
    @abstractmethod
    def synthesize_executive_narrative(
        self, problem_title: str, kpi: KPISummary, root_cause_summary: str
    ) -> str:
        """Translates computed findings into crisp, executive-ready consulting language."""
        pass
        
    @abstractmethod
    def formulate_hypotheses(
        self, anomalies: List[Dict[str, Any]], context: Dict[str, Any]
    ) -> List[ExecutiveInsight]:
        """Formulates verifiable business hypotheses for validation."""
        pass
