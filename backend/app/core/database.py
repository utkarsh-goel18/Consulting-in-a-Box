import os
import duckdb
import pandas as pd
from typing import Dict, Any, Optional
from sqlalchemy import create_engine, text
from app.core.config import settings

class DataRepository:
    """
    Unified Data Repository providing dual-engine access:
    1. In-process DuckDB for lightning-fast OLAP analysis on CSVs and DataFrames
    2. SQLAlchemy connection for enterprise PostgreSQL integration
    """
    _instance = None

    def __init__(self):
        self.dataframes: Dict[str, pd.DataFrame] = {}
        self.duck_conn = duckdb.connect(database=":memory:")
        self.pg_engine = None
        self._init_pg()
        
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _init_pg(self):
        if settings.DATABASE_URL:
            try:
                self.pg_engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
            except Exception:
                self.pg_engine = None

    def check_postgres(self) -> Dict[str, Any]:
        if not self.pg_engine:
            return {"connected": False, "message": "No DATABASE_URL configured"}
        try:
            with self.pg_engine.connect() as conn:
                res = conn.execute(text("SELECT version();")).fetchone()
                return {"connected": True, "version": str(res[0])}
        except Exception as e:
            return {"connected": False, "error": str(e)}

    def register_dataframe(self, name: str, df: pd.DataFrame):
        self.dataframes[name] = df
        try:
            self.duck_conn.register(name, df)
        except Exception:
            pass

    def load_from_directory(self, dir_path: str = None):
        target_dir = dir_path or settings.DATA_DIR
        if not os.path.exists(target_dir):
            return
            
        for file in os.listdir(target_dir):
            if file.endswith(".csv"):
                table_name = os.path.splitext(file)[0]
                file_path = os.path.join(target_dir, file)
                try:
                    df = pd.read_csv(file_path)
                    self.register_dataframe(table_name, df)
                except Exception as e:
                    print(f"Error loading {file}: {e}")

    def query_sql(self, sql: str) -> pd.DataFrame:
        """Executes analytical SQL query against loaded tables via DuckDB."""
        return self.duck_conn.execute(sql).df()

repo = DataRepository.get_instance()
