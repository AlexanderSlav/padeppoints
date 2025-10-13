"""add_court_number_to_rounds

Revision ID: b470aa95ad2a
Revises: 99caa5e3c563
Create Date: 2025-10-12 12:53:49.201974

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b470aa95ad2a'
down_revision: Union[str, None] = '99caa5e3c563'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add court_number column to rounds table
    op.add_column('rounds', sa.Column('court_number', sa.Integer(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove court_number column from rounds table
    op.drop_column('rounds', 'court_number')
