"""add join code to tournaments

Revision ID: c3a5d4e5f6a7
Revises: 908cf7ecefe9
Create Date: 2025-09-13 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'c3a5d4e5f6a7'
down_revision = '908cf7ecefe9'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('tournaments', sa.Column('join_code', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('tournaments', 'join_code')
