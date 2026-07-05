from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.routes import cleaning, datasets, eda, features, projects, training
from app.database.connection import check_database_connection
from app.database.init_db import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    check_database_connection()
    yield


app = FastAPI(
    title="MLForge AI API",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(projects.router)
app.include_router(datasets.router)
app.include_router(eda.router)
app.include_router(cleaning.router)
app.include_router(features.router)
app.include_router(training.router)

ROOT_DIR = Path(__file__).resolve().parents[2]
FRONTEND_PUBLIC_DIR = ROOT_DIR / "frontend" / "public"
REPORTS_DIR = Path(__file__).resolve().parent / "storage" / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

if FRONTEND_PUBLIC_DIR.exists():
    app.mount("/ui", StaticFiles(directory=FRONTEND_PUBLIC_DIR, html=True), name="ui")

app.mount("/reports", StaticFiles(directory=REPORTS_DIR), name="reports")


@app.get("/")
def read_root() -> dict[str, str]:
    return {
        "app": "MLForge AI API",
        "database": "connected",
    }
