from app.core.config import settings
from app.ai.base import BaseAIProvider
from app.ai.mock_consultant import MockStrategicConsultant
from app.ai.gemini_provider import GeminiAIProvider

def get_ai_provider() -> BaseAIProvider:
    if settings.AI_PROVIDER == "gemini" and settings.GEMINI_API_KEY:
        return GeminiAIProvider(api_key=settings.GEMINI_API_KEY, model=settings.AI_MODEL)
    # Default to deterministic mock consultant (works completely offline / demo mode)
    return MockStrategicConsultant()
