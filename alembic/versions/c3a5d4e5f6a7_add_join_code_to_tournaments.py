"""add join code to tournaments

Revision ID: c3a5d4e5f6a7
Revises: f721ad6d988b
Create Date: 2025-09-29 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c3a5d4e5f6a7'
down_revision: Union[str, None] = 'f721ad6d988b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add join_code column to tournaments."""
    op.add_column('tournaments', sa.Column('join_code', sa.String(), nullable=True))
    op.create_unique_constraint('uq_tournaments_join_code', 'tournaments', ['join_code'])


def downgrade() -> None:
    """Remove join_code column from tournaments."""
    op.drop_constraint('uq_tournaments_join_code', 'tournaments', type_='unique')
    op.drop_column('tournaments', 'join_code')

