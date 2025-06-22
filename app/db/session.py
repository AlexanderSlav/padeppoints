"""Engine module for the database."""

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine


async def configure_db(dsn: str, is_prod: bool = True) -> AsyncEngine:
    """Configure app db connection and session maker."""
    engine = create_async_engine(dsn, echo=not is_prod)
    logger.info("DB connection created.")
    return engine


async def disconnect_from_db(engine: AsyncEngine):
    """Disconnect app from DB."""
    await engine.dispose()
    logger.info("DB disconnected.")
