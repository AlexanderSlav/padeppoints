"""make email nullable for guest users

Revision ID: f721ad6d988b
Revises: b25bc8687934
Create Date: 2025-07-27 14:25:13.434227

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f721ad6d988b'
down_revision: Union[str, None] = 'b25bc8687934'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Make email column nullable to support guest users
    op.alter_column('users', 'email',
                    existing_type=sa.VARCHAR(),
                    nullable=True)


def downgrade() -> None:
    """Downgrade schema."""
    # Make email column NOT NULL again (only if no NULL values exist)
    op.alter_column('users', 'email',
                    existing_type=sa.VARCHAR(),
                    nullable=False)
