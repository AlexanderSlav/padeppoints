"""add_gender_to_users

Revision ID: 99caa5e3c563
Revises: e9d2657fba5a
Create Date: 2025-10-12 12:11:57.361695

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '99caa5e3c563'
down_revision: Union[str, None] = 'e9d2657fba5a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create the gender enum type
    gender_enum = sa.Enum('MALE', 'FEMALE', 'OTHER', 'PREFER_NOT_TO_SAY', name='gender')
    gender_enum.create(op.get_bind(), checkfirst=True)

    # Add the column
    op.add_column('users', sa.Column('gender', gender_enum, nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    # Drop the column
    op.drop_column('users', 'gender')

    # Drop the enum type
    sa.Enum(name='gender').drop(op.get_bind(), checkfirst=True)
