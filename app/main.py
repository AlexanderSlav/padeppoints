"""Entrypoint for the API."""
from contextlib import asynccontextmanager
from app.migration import run_migrations

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.openapi.utils import get_openapi
from loguru import logger
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.api import api_router
from app.core.config import settings
from app.db.session import configure_db, disconnect_from_db
from sqlalchemy.ext.asyncio import AsyncEngine

limiter = Limiter(key_func=get_remote_address)

@asynccontextmanager
async def lifespan(highlights_app: FastAPI):
    """Lifespan events."""
    engine: AsyncEngine = await configure_db(settings.db.dsn, is_prod=False)

    logger.info(f"Starting {highlights_app.title}.")

    try:
        run_migrations(settings.db.dsn)  # sync is fine here, see migration.py
    except Exception as exc:
        logger.error(f"Alembic migration error: {exc}.")

    logger.info("Application startup complete.")

    yield

    logger.info(f"Ending {highlights_app.title}.")

    await disconnect_from_db(engine)


app = FastAPI(
    title="Tornetic API",
    description="Padel Tournament Management System",
    version="0.1.0",
    lifespan=lifespan,
    # Trust proxy headers for correct scheme detection
    root_path="",
)

# Middleware to handle proxy headers (X-Forwarded-Proto, X-Forwarded-For, etc.)
@app.middleware("http")
async def proxy_headers_middleware(request: Request, call_next):
    """Handle X-Forwarded-* headers from reverse proxy."""
    # Get the forwarded protocol (http or https)
    forwarded_proto = request.headers.get("x-forwarded-proto")
    if forwarded_proto:
        # Override the URL scheme if behind a proxy
        request.scope["scheme"] = forwarded_proto

    response = await call_next(request)
    return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins in development
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
    expose_headers=["*"],
)

# Rate limiting
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.middleware("http")
async def exception_handler(request: Request, call_next):
    """Global exception handler middleware."""
    try:
        return await call_next(request)
    except HTTPException:
        raise
    except Exception as err:
        logger.error(f"Unhandled error: {err}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error", "code": 500}
        )

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Tornetic API is running"}

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "healthy", "service": "tornetic-api"}

app.include_router(api_router, prefix="/api/v1") 