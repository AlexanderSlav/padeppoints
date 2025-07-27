"""Alembic environment file."""

import os
from logging.config import fileConfig

from dotenv import load_dotenv
from sqlalchemy import create_engine

from alembic import context
from app.models import *

load_dotenv()

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def get_sync_url() -> str:
    """Get synchronous database URL."""
    url_tokens: dict = {
        "DB_USERNAME": os.environ["DB_USERNAME"],
        "DB_PASSWORD": os.environ["DB_PASSWORD"],
        "DB_NAME": os.environ["DB_NAME"],
        "DB_HOSTNAME": os.environ["DB_HOSTNAME"],
        "DB_PORT": os.environ["DB_PORT"],
    }

    # Build sync URL directly
    return f"postgresql://{url_tokens['DB_USERNAME']}:{url_tokens['DB_PASSWORD']}@{url_tokens['DB_HOSTNAME']}:{url_tokens['DB_PORT']}/{url_tokens['DB_NAME']}"


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = get_sync_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    url = get_sync_url()
    connectable = create_engine(url)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
