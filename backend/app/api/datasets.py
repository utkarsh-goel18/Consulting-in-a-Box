import os
import pandas as pd
from typing import List, Dict, Any
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.core.config import settings
from app.core.database import repo
from app.engine.profiler import profile_dataframe, detect_relationships
from app.models.schemas import DatasetsOverview, DatasetProfile

router = APIRouter(prefix="/datasets", tags=["datasets"])

@router.get("/overview", response_model=DatasetsOverview)
def get_datasets_overview():
    """Returns profiling statistics, quality score, and PK/FK relations across all ingested datasets."""
    # Ensure datasets are loaded
    if not repo.dataframes:
        repo.load_from_directory()
        
    profiles: List[DatasetProfile] = []
    for name, df in repo.dataframes.items():
        file_name = f"{name}.csv"
        file_path = os.path.join(settings.DATA_DIR, file_name)
        file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
        profiles.append(profile_dataframe(name, file_name, df, file_size))
        
    relationships = detect_relationships(repo.dataframes)
    
    overall_quality = round(sum(p.data_quality_score for p in profiles) / max(len(profiles), 1), 1) if profiles else 0.0
    
    return DatasetsOverview(
        datasets=profiles,
        relationships=relationships,
        overall_quality_score=overall_quality
    )

@router.post("/upload", response_model=DatasetProfile)
async def upload_dataset(file: UploadFile = File(...)):
    """Uploads and profiles a new CSV or XLSX dataset."""
    filename = file.filename
    ext = os.path.splitext(filename)[1].lower()
    if ext not in [".csv", ".xlsx", ".xls"]:
        raise HTTPException(status_code=400, detail="Only CSV and Excel (XLSX) files are supported.")
        
    save_path = os.path.join(settings.DATA_DIR, filename)
    content = await file.read()
    with open(save_path, "wb") as f:
        f.write(content)
        
    table_name = os.path.splitext(filename)[0]
    try:
        if ext == ".csv":
            df = pd.read_csv(save_path)
        else:
            df = pd.read_excel(save_path)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse file: {str(e)}")
        
    repo.register_dataframe(table_name, df)
    return profile_dataframe(table_name, filename, df, len(content))

@router.get("/{name}/preview")
def get_table_preview(name: str):
    """Returns sample records and column headers for a dataset."""
    if name not in repo.dataframes:
        raise HTTPException(status_code=404, detail=f"Dataset {name} not found.")
    df = repo.dataframes[name]
    sample = df.head(100).fillna("").to_dict(orient="records")
    return {
        "dataset_name": name,
        "total_rows": len(df),
        "columns": list(df.columns),
        "records": sample
    }
