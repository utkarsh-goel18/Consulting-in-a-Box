import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import repo
from app.engine.demo_data import generate_datasets
from app.api.demo import router as demo_router
from app.api.datasets import router as datasets_router
from app.api.analysis import router as analysis_router
from app.api.insights import router as insights_router
from app.api.scenarios import router as scenarios_router
from app.api.reports import router as reports_router
from app.api.settings import router as settings_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the complete demo dataset once at startup. Previously the startup
    # check only required three files, which could cause /demo/bootstrap to
    # regenerate every dataset when one auxiliary CSV was missing.
    os.makedirs(settings.DATA_DIR, exist_ok=True)
    required = [
        "customers.csv",
        "orders.csv",
        "products.csv",
        "order_items.csv",
        "marketing_spend.csv",
        "expenses.csv",
        "returns.csv",
    ]
    if not all(os.path.exists(os.path.join(settings.DATA_DIR, f)) for f in required):
        print("Generating initial synthetic NovaMart demo dataset...")
        generate_datasets(settings.DATA_DIR, scale="demo")

    repo.load_from_directory(settings.DATA_DIR)
    print(f"Loaded {len(repo.dataframes)} tables into memory & DuckDB analytical engine.")
    yield

app = FastAPI(
    title="Consulting in a Box API",
    description="Automated Decision Intelligence & Consulting Engine",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(demo_router, prefix="/api")
app.include_router(datasets_router, prefix="/api")
app.include_router(analysis_router, prefix="/api")
app.include_router(insights_router, prefix="/api")
app.include_router(scenarios_router, prefix="/api")
app.include_router(reports_router, prefix="/api")
app.include_router(settings_router, prefix="/api")

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "Consulting in a Box",
        "loaded_tables": list(repo.dataframes.keys()),
        "engine": "DuckDB + Python Analytical Engine"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
