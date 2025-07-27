"""Alembic migration module."""

from loguru import logger

from alembic import command
from alembic.config import Config


def run_migrations(pg_dsn: str) -> None:
    """Runs migrations."""
    # Convert async DSN to sync DSN for alembic
    sync_dsn = pg_dsn.replace("postgresql+asyncpg://", "postgresql://")
    alembic_conf = Config("alembic.ini")
    alembic_conf.attributes["configure_logger"] = False
    alembic_conf.set_main_option("sqlalchemy.url", sync_dsn)

    target_revision: str = "head"

    logger.info(f"Applying alembic migration <{target_revision}>.")

    # Target the most recent revision(s) -> "head".
    command.upgrade(alembic_conf, target_revision)

    logger.info("Finishing applying revisions.")
