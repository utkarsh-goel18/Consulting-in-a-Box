import os
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Tuple
from app.models.schemas import (
    ColumnProfile, DatasetProfile, DetectedRelationship, DatasetsOverview, ColumnType
)


def infer_column_type(col_name: str, series: pd.Series) -> ColumnType:
    col_lower = col_name.lower()

    if col_lower.endswith("_id") or col_lower == "id" or col_lower.endswith("id") or col_lower == "sku":
        return ColumnType.ID

    if pd.api.types.is_bool_dtype(series):
        return ColumnType.BOOLEAN

    if pd.api.types.is_datetime64_any_dtype(series):
        return ColumnType.DATETIME
    if "date" in col_lower or "time" in col_lower or "timestamp" in col_lower:
        sample = series.dropna().head(10)
        if len(sample) > 0:
            try:
                pd.to_datetime(sample)
                return ColumnType.DATETIME
            except Exception:
                pass

    if pd.api.types.is_numeric_dtype(series):
        return ColumnType.NUMERIC

    unique_count = series.nunique(dropna=True)
    total_count = len(series.dropna())
    if total_count > 0 and (unique_count / total_count < 0.2 or unique_count <= 50):
        return ColumnType.CATEGORICAL

    return ColumnType.TEXT


def profile_dataframe(name: str, file_name: str, df: pd.DataFrame, file_size_bytes: int = 0) -> DatasetProfile:
    """Profile a dataframe while avoiding expensive full-frame operations on large tables."""
    row_count = len(df)
    column_count = len(df.columns)
    column_profiles: List[ColumnProfile] = []
    likely_pks: List[str] = []
    total_cells = max(row_count * column_count, 1)
    total_missing = 0

    # Full-frame duplicated() becomes unnecessarily expensive for 500k+ row tables.
    # A bounded sample is sufficient for the quality indicator because primary-key
    # uniqueness is checked separately below.
    if row_count > 100_000:
        sample_size = min(50_000, row_count)
        sample = df.iloc[:sample_size]
        duplicate_rows = int(sample.duplicated().sum() * (row_count / sample_size))
    else:
        duplicate_rows = int(df.duplicated().sum())

    for col in df.columns:
        series = df[col]
        dtype = infer_column_type(col, series)
        raw_dtype = str(series.dtype)
        missing_count = int(series.isna().sum())
        total_missing += missing_count
        missing_pct = round((missing_count / max(row_count, 1)) * 100, 2)
        unique_count = int(series.nunique(dropna=True))
        is_unique = unique_count == row_count and missing_count == 0

        if (is_unique or (unique_count >= row_count * 0.999 and missing_count == 0)) and (
            dtype == ColumnType.ID or col.lower().endswith("id") or col.lower() == "sku"
        ):
            likely_pks.append(col)

        sample_vals = [str(v) for v in series.dropna().head(5).tolist()]
        min_val = None
        max_val = None
        mean_val = None

        if pd.api.types.is_numeric_dtype(series) and series.dropna().shape[0] > 0:
            min_raw = series.min()
            max_raw = series.max()
            min_val = float(min_raw) if pd.notna(min_raw) else None
            max_val = float(max_raw) if pd.notna(max_raw) else None
            mean_raw = series.mean()
            mean_val = round(float(mean_raw), 2) if pd.notna(mean_raw) else None

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

    completeness_score = max(0, 100 - (total_missing / total_cells * 100) * 2)
    uniqueness_score = max(0, 100 - (duplicate_rows / max(row_count, 1) * 100) * 5)
    pk_bonus = 5 if likely_pks else 0
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
    """Infer FK relationships without repeatedly materializing huge Python sets.

    For large tables, compare only columns with the same normalized name and use
    pandas' vectorized isin() against a unique target key. This keeps the Data page
    responsive for the 500k-order NovaMart fixture.
    """
    relationships: List[DetectedRelationship] = []
    dataset_keys = list(dataframes.keys())
    seen_pairs = set()

    for src_name in dataset_keys:
        src_df = dataframes[src_name]
        if src_df.empty:
            continue
        for col in src_df.columns:
            col_lower = str(col).lower()
            if not (col_lower.endswith("_id") or col_lower == "id" or col_lower == "sku"):
                continue

            for tgt_name in dataset_keys:
                if src_name == tgt_name:
                    continue
                tgt_df = dataframes[tgt_name]
                if tgt_df.empty:
                    continue

                target_candidates = [c for c in tgt_df.columns if str(c).lower() == col_lower]
                for tgt_col in target_candidates:
                    pair = (src_name, col, tgt_name, tgt_col)
                    reverse = (tgt_name, tgt_col, src_name, col)
                    if pair in seen_pairs or reverse in seen_pairs:
                        continue

                    src_series = src_df[col].dropna()
                    tgt_series = tgt_df[tgt_col].dropna()
                    if src_series.empty or tgt_series.empty:
                        continue

                    # Avoid a costly exact uniqueness calculation for giant target tables
                    # when the source itself is clearly a foreign-key-like column.
                    tgt_unique_count = int(tgt_series.nunique())
                    tgt_is_unique = tgt_unique_count == len(tgt_series)

                    # Bound the source side for very large fact tables. The relationship
                    # confidence is directional but only used as a UI heuristic.
                    if len(src_series) > 100_000:
                        src_check = src_series.iloc[:100_000]
                    else:
                        src_check = src_series

                    match_rate = float(src_check.isin(tgt_series).mean() * 100)
                    if match_rate <= 50.0:
                        continue

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
                    seen_pairs.add(pair)

    return relationships
