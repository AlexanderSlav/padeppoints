"""Entrypoint for the API."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from loguru import logger

from app.api.v1.api import api_router
from app.core.config import settings
from app.core.middleware import setup_middleware
from app.db.session import configure_db, disconnect_from_db
from app.migration import run_migrations

@asynccontextmanager
async def lifespan(highlights_app: FastAPI):
    """Lifespan events."""
    engine = await configure_db(settings.db.dsn, is_prod=False)

    logger.info(f"Starting {highlights_app.title}.")

    try:
        run_migrations(settings.db.dsn)  # sync is fine here, see migration.py
    except Exception as exc:
        logger.error(f"Alembic migration error: {exc}.")

    yield

    logger.info(f"Ending {highlights_app.title}.")

    await disconnect_from_db(engine)


app = FastAPI(
    title="Tornetic API",
    description="Padel Tournament Management System",
    version="0.1.0",
    lifespan=lifespan,
)

# Configure all middleware
setup_middleware(app)

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Tornetic API is running"}

app.include_router(api_router, prefix="/api/v1") 