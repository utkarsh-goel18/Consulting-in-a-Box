from __future__ import annotations

import os
import pandas as pd
from typing import List
from fastapi import APIRouter, UploadFile, File, HTTPException

from app.core.analysis_service import invalidate
from app.core.config import settings
from app.core.database import repo
from app.engine.profiler import profile_dataframe, detect_relationships
from app.models.schemas import DatasetsOverview, DatasetProfile

router = APIRouter(prefix="/datasets", tags=["datasets"])


@router.get("/overview", response_model=DatasetsOverview)
def get_datasets_overview():
    """Return dataset profiles, quality indicators and inferred entity relationships."""
    if not repo.dataframes:
        repo.load_from_directory()

    profiles: List[DatasetProfile] = []
    for name, df in repo.dataframes.items():
        file_path = os.path.join(settings.DATA_DIR, f"{name}.csv")
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
        profiles.append(profile_dataframe(name, file_name, df, file_size))

    relationships = detect_relationships(repo.dataframes)
    overall_quality = round(sum(p.data_quality_score for p in profiles) / max(len(profiles), 1), 1) if profiles else 0.0
    return DatasetsOverview(datasets=profiles, relationships=relationships, overall_quality_score=overall_quality)


@router.post("/upload", response_model=DatasetProfile)
async def upload_dataset(file: UploadFile = File(...)):
    """Ingest a CSV/XLSX, profile it, register it in DuckDB and invalidate analytical caches."""
    filename = os.path.basename(file.filename or "")
    ext = os.path.splitext(filename)[1].lower()
    if ext not in {".csv", ".xlsx", ".xls"}:
        raise HTTPException(status_code=400, detail="Only CSV and Excel (XLSX/XLS) files are supported.")
    if not filename or filename.startswith("."):
        raise HTTPException(status_code=400, detail="A valid dataset filename is required.")

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="The uploaded file is empty.")

    save_path = os.path.join(settings.DATA_DIR, filename)
    with open(save_path, "wb") as handle:
        handle.write(content)

    table_name = os.path.splitext(filename)[0]
    try:
        df = pd.read_csv(save_path) if ext == ".csv" else pd.read_excel(save_path)
    except Exception as exc:
        try:
            os.remove(save_path)
        except OSError:
            pass
        raise HTTPException(status_code=400, detail=f"Failed to parse file: {exc}") from exc

    repo.register_dataframe(table_name, df)
    invalidate()
    cache_path = os.path.join(settings.DATA_DIR, ".novamart_dashboard_cache.json")
    try:
        os.remove(cache_path)
    except OSError:
        pass
    return profile_dataframe(table_name, filename, df, len(content))


@router.get("/{name}/preview")
def get_table_preview(name: str):
    """Return the first 100 records for interactive inspection."""
    if name not in repo.dataframes:
        raise HTTPException(status_code=404, detail=f"Dataset {name} not found.")
    df = repo.dataframes[name]
    return {
        "dataset_name": name,
        "total_rows": len(df),
        "columns": list(df.columns),
        "records": df.head(100).fillna("").to_dict(orient="records"),
    }
