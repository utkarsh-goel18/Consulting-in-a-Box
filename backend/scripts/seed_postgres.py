import os
import sys
import pandas as pd
from sqlalchemy import create_engine, text

# Add backend directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.core.config import settings

def seed_postgres(database_url: str = None, data_dir: str = None):
    db_url = database_url or settings.DATABASE_URL
    d_dir = data_dir or settings.DATA_DIR
    
    print(f"Connecting to PostgreSQL at {db_url}...")
    try:
        engine = create_engine(db_url)
        schema_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../sql/schema.sql"))
        
        with open(schema_path, "r", encoding="utf-8") as f:
            ddl = f.read()
            
        print("Executing schema DDL...")
        with engine.connect() as conn:
            conn.execute(text(ddl))
            conn.commit()
        print("✓ PostgreSQL Schema created successfully.")
        
        # Load tables in dependency order
        table_files = [
            ("customers", "customers.csv"),
            ("products", "products.csv"),
            ("orders", "orders.csv"),
            ("order_items", "order_items.csv"),
            ("marketing_spend", "marketing_spend.csv"),
            ("expenses", "expenses.csv"),
            ("returns", "returns.csv")
        ]
        
        for table_name, file_name in table_files:
            f_path = os.path.join(d_dir, file_name)
            if os.path.exists(f_path):
                print(f"Loading {file_name} into {table_name}...")
                df = pd.read_csv(f_path)
                df.to_sql(table_name, engine, if_exists="append", index=False, chunksize=5000)
                print(f"✓ Seeded {len(df)} rows into {table_name}")
            else:
                print(f"File {f_path} not found. Skipping.")
                
        print("\n✓ PostgreSQL seeding completed successfully!")
    except Exception as e:
        print(f"PostgreSQL seed failed or skipped: {e}")
        print("Application will default to high-performance DuckDB / In-Memory analytical engine.")

if __name__ == "__main__":
    seed_postgres()
