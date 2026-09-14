import os
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Tuple
from app.models.schemas import (
    ColumnProfile, DatasetProfile, DetectedRelationship, DatasetsOverview, ColumnType
)

def infer_column_type(col_name: str, series: pd.Series) -> ColumnType:
    col_lower = col_name.lower()
    
    # ID heuristics
    if col_lower.endswith("_id") or col_lower == "id" or col_lower.endswith("id") or col_lower == "sku":
        return ColumnType.ID
        
    # Boolean
    if pd.api.types.is_bool_dtype(series):
        return ColumnType.BOOLEAN
        
    # Datetime
    if pd.api.types.is_datetime64_any_dtype(series):
        return ColumnType.DATETIME
    if "date" in col_lower or "time" in col_lower or "timestamp" in col_lower:
        # Try sample parsing
        sample = series.dropna().head(10)
        if len(sample) > 0:
            try:
                pd.to_datetime(sample)
                return ColumnType.DATETIME
            except Exception:
                pass

    # Numeric
    if pd.api.types.is_numeric_dtype(series):
        return ColumnType.NUMERIC
        
    # Categorical vs Text
    unique_count = series.nunique(dropna=True)
    total_count = len(series.dropna())
    if total_count > 0 and (unique_count / total_count < 0.2 or unique_count <= 50):
        return ColumnType.CATEGORICAL
        
    return ColumnType.TEXT

def profile_dataframe(name: str, file_name: str, df: pd.DataFrame, file_size_bytes: int = 0) -> DatasetProfile:
    row_count = len(df)
    column_count = len(df.columns)
    
    column_profiles: List[ColumnProfile] = []
    likely_pks: List[str] = []
    
    total_cells = max(row_count * column_count, 1)
    total_missing = 0
    duplicate_rows = df.duplicated().sum()
    
    for col in df.columns:
        series = df[col]
        dtype = infer_column_type(col, series)
        raw_dtype = str(series.dtype)
        missing_count = int(series.isna().sum())
        total_missing += missing_count
        missing_pct = round((missing_count / max(row_count, 1)) * 100, 2)
        unique_count = int(series.nunique(dropna=True))
        is_unique = (unique_count == row_count and missing_count == 0)
        
        # Primary key candidate heuristic
        if (is_unique or (unique_count >= row_count * 0.999 and missing_count == 0)) and (
            dtype == ColumnType.ID or col.lower().endswith("id") or col.lower() == "sku"
        ):
            likely_pks.append(col)
            
        sample_vals = [str(v) for v in series.dropna().head(5).tolist()]
        min_val = None
        max_val = None
        mean_val = None
        
        if pd.api.types.is_numeric_dtype(series) and series.dropna().shape[0] > 0:
            min_val = float(series.min()) if not np.isnan(series.min()) else None
            max_val = float(series.max()) if not np.isnan(series.max()) else None
            mean_val = round(float(series.mean()), 2) if not np.isnan(series.mean()) else None

        column_profiles.append(ColumnProfile(
            name=str(col),
            dtype=dtype,
            raw_dtype=raw_dtype,
            total_count=row_count,
            missing_count=missing_count,
            missing_pct=missing_pct,
            unique_count=unique_count,
            is_unique=is_unique,
            sample_values=sample_vals,
            min_val=min_val,
            max_val=max_val,
            mean_val=mean_val
        ))
        
    # Calculate Data Quality Score (0-100)
    completeness_score = max(0, 100 - (total_missing / total_cells * 100) * 2)
    uniqueness_score = max(0, 100 - (duplicate_rows / max(row_count, 1) * 100) * 5)
    pk_bonus = 5 if len(likely_pks) > 0 else 0
    data_quality_score = min(100.0, round(completeness_score * 0.6 + uniqueness_score * 0.35 + pk_bonus, 1))
    
    return DatasetProfile(
        dataset_name=name,
        file_name=file_name,
        row_count=row_count,
        column_count=column_count,
        data_quality_score=data_quality_score,
        likely_primary_keys=likely_pks,
        columns=column_profiles,
        file_size_bytes=file_size_bytes
    )

def detect_relationships(dataframes: Dict[str, pd.DataFrame]) -> List[DetectedRelationship]:
    relationships: List[DetectedRelationship] = []
    dataset_keys = list(dataframes.keys())
    
    for i in range(len(dataset_keys)):
        for j in range(len(dataset_keys)):
            if i == j:
                continue
            src_name = dataset_keys[i]
            tgt_name = dataset_keys[j]
            src_df = dataframes[src_name]
            tgt_df = dataframes[tgt_name]
            
            for col in src_df.columns:
                col_lower = str(col).lower()
                # Check potential foreign key relation
                if col_lower.endswith("_id") or col_lower == "id" or col_lower == "sku":
                    # Check if target dataset has exact column or matching id
                    target_candidates = [c for c in tgt_df.columns if c.lower() == col_lower or (col_lower == f"{tgt_name.rstrip('s')}_id" and c.lower() == f"{tgt_name.rstrip('s')}_id")]
                    for tgt_col in target_candidates:
                        src_vals = set(src_df[col].dropna().unique())
                        tgt_vals = set(tgt_df[tgt_col].dropna().unique())
                        if len(src_vals) > 0 and len(tgt_vals) > 0:
                            intersection = src_vals.intersection(tgt_vals)
                            match_rate = len(intersection) / len(src_vals) * 100
                            if match_rate > 50.0:
                                # Determine cardinality
                                tgt_is_unique = (tgt_df[tgt_col].nunique() == len(tgt_df))
                                rel_type = "N:1" if tgt_is_unique else "N:N"
                                confidence = "High" if match_rate > 90 else "Medium"
                                
                                relationships.append(DetectedRelationship(
                                    source_dataset=src_name,
                                    source_column=col,
                                    target_dataset=tgt_name,
                                    target_column=tgt_col,
                                    relationship_type=rel_type,
                                    match_rate_pct=round(match_rate, 1),
                                    confidence=confidence
                                ))
    return relationships
