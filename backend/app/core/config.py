import os
from pydantic import BaseModel
from typing import Optional

class Settings(BaseModel):
    PROJECT_NAME: str = "Consulting in a Box"
    API_V1_STR: str = "/api"
    DEMO_MODE: bool = True
    
    # Storage paths
    DATA_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data"))
    REPORTS_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../reports_out"))
    
    # Optional PostgreSQL connection
    DATABASE_URL: Optional[str] = os.getenv(
        "DATABASE_URL", 
        "postgresql://postgres:postgres@localhost:5432/consulting_box"
    )
    
    # AI Provider configuration (mock, gemini, openai, anthropic)
    AI_PROVIDER: str = os.getenv("AI_PROVIDER", "mock")
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY", None)
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY", None)
    AI_MODEL: str = os.getenv("AI_MODEL", "gemini-1.5-flash")

    class Config:
        arbitrary_types_allowed = True

settings = Settings()
os.makedirs(settings.DATA_DIR, exist_ok=True)
os.makedirs(settings.REPORTS_DIR, exist_ok=True)
