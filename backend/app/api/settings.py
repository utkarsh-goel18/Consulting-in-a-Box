import os
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, Dict, Any
from app.core.config import settings
from app.core.database import repo

router = APIRouter(prefix="/settings", tags=["settings"])

class SettingsUpdate(BaseModel):
    demo_mode: Optional[bool] = None
    ai_provider: Optional[str] = None # 'mock' or 'gemini' or 'openai'
    gemini_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    ai_model: Optional[str] = None
    database_url: Optional[str] = None

@router.get("")
def get_system_settings():
    pg_status = repo.check_postgres()
    return {
        "project_name": settings.PROJECT_NAME,
        "demo_mode": settings.DEMO_MODE,
        "ai_provider": settings.AI_PROVIDER,
        "ai_model": settings.AI_MODEL,
        "has_gemini_key": bool(settings.GEMINI_API_KEY),
        "has_openai_key": bool(settings.OPENAI_API_KEY),
        "database_url_configured": bool(settings.DATABASE_URL),
        "postgres_status": pg_status,
        "data_directory": settings.DATA_DIR,
        "loaded_tables": list(repo.dataframes.keys())
    }

@router.post("")
def update_system_settings(req: SettingsUpdate):
    if req.demo_mode is not None:
        settings.DEMO_MODE = req.demo_mode
    if req.ai_provider is not None:
        settings.AI_PROVIDER = req.ai_provider
    if req.gemini_api_key is not None and req.gemini_api_key.strip():
        settings.GEMINI_API_KEY = req.gemini_api_key.strip()
    if req.openai_api_key is not None and req.openai_api_key.strip():
        settings.OPENAI_API_KEY = req.openai_api_key.strip()
    if req.ai_model is not None:
        settings.AI_MODEL = req.ai_model
    if req.database_url is not None:
        settings.DATABASE_URL = req.database_url
        repo._init_pg()
        
    return {"status": "success", "message": "Settings updated successfully"}
