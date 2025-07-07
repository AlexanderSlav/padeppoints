"""add auth fields to user

Revision ID: b4a1b4c3c9bd
Revises: 909f6c9d5461
Create Date: 2025-07-05 00:00:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'b4a1b4c3c9bd'
down_revision: Union[str, None] = '909f6c9d5461'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('hashed_password', sa.String(), nullable=True))
    op.add_column('users', sa.Column('is_verified', sa.Boolean(), nullable=True, server_default=sa.false()))


def downgrade() -> None:
    op.drop_column('users', 'is_verified')
    op.drop_column('users', 'hashed_password')
