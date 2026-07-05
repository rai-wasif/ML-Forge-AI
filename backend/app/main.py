from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database.connection import check_database_connection


@asynccontextmanager
async def lifespan(app: FastAPI):
    check_database_connection()
    yield


app = FastAPI(
    title="MLForge AI API",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/")
def read_root() -> dict[str, str]:
    return {
        "app": "MLForge AI API",
        "database": "connected",
    }
