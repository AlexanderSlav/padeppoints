"""add missing tournament fields

Revision ID: b25bc8687934
Revises: b4a1b4c3c9bd
Create Date: 2025-07-27 14:21:40.235431

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b25bc8687934'
down_revision: Union[str, None] = 'b4a1b4c3c9bd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add missing columns to tournaments table
    op.add_column('tournaments', sa.Column('points_per_match', sa.Integer(), nullable=False, server_default='32'))
    op.add_column('tournaments', sa.Column('courts', sa.Integer(), nullable=False, server_default='1'))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove the added columns
    op.drop_column('tournaments', 'courts')
    op.drop_column('tournaments', 'points_per_match')
