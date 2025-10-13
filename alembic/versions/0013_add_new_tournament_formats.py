"""add_new_tournament_formats

Revision ID: c5d8f3a12b4e
Revises: b470aa95ad2a
Create Date: 2025-10-12 16:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c5d8f3a12b4e'
down_revision: Union[str, None] = 'b470aa95ad2a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # PostgreSQL enum requires special handling
    # Add new values to the tournamentsystem enum
    op.execute("ALTER TYPE tournamentsystem ADD VALUE IF NOT EXISTS 'MEXICANO'")
    op.execute("ALTER TYPE tournamentsystem ADD VALUE IF NOT EXISTS 'TEAM_AMERICANO'")
    op.execute("ALTER TYPE tournamentsystem ADD VALUE IF NOT EXISTS 'TEAM_MEXICANO'")
    op.execute("ALTER TYPE tournamentsystem ADD VALUE IF NOT EXISTS 'BEAT_THE_BOX'")


def downgrade() -> None:
    """Downgrade schema."""
    # Cannot remove enum values in PostgreSQL without recreating the enum
    # This would require dropping and recreating the tournaments table
    # For safety, we'll leave the enum values in place
    pass
