"""Middleware configuration for the FastAPI application."""
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from app.core.config import settings


def setup_cors(app: FastAPI) -> None:
    """Configure CORS middleware."""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
    )


def setup_rate_limiting(app: FastAPI) -> None:
    """Configure rate limiting middleware."""
    limiter = Limiter(key_func=get_remote_address)
    app.state.limiter = limiter
    app.add_middleware(SlowAPIMiddleware)
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


async def global_exception_handler(request: Request, call_next):
    """Global exception handler middleware."""
    try:
        return await call_next(request)
    except HTTPException:
        raise
    except Exception as err:
        logger.error(f"Unhandled error on {request.method} {request.url}: {err}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error", "code": 500}
        )


def setup_middleware(app: FastAPI) -> None:
    """Configure all middleware for the application."""
    setup_cors(app)
    setup_rate_limiting(app)
    
    # Add global exception handler
    app.middleware("http")(global_exception_handler)