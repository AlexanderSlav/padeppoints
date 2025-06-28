"""rename table

Revision ID: a53d6a5eb83b
Revises: edfa76be39f6
Create Date: 2025-06-28 14:09:55.851509

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'a53d6a5eb83b'
down_revision: Union[str, None] = 'edfa76be39f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Simply rename the table instead of creating a new one
    op.rename_table('tournament', 'tournaments')
    
    # Update foreign key constraints to point to the renamed table
    op.drop_constraint('rounds_tournament_id_fkey', 'rounds', type_='foreignkey')
    op.create_foreign_key(None, 'rounds', 'tournaments', ['tournament_id'], ['id'])
    op.drop_constraint('tournament_player_tournament_id_fkey', 'tournament_player', type_='foreignkey')
    op.create_foreign_key(None, 'tournament_player', 'tournaments', ['tournament_id'], ['id'])


def downgrade() -> None:
    """Downgrade schema."""
    # Reverse the process: rename back and restore foreign keys
    op.drop_constraint(None, 'tournament_player', type_='foreignkey')
    op.create_foreign_key('tournament_player_tournament_id_fkey', 'tournament_player', 'tournament', ['tournament_id'], ['id'])
    op.drop_constraint(None, 'rounds', type_='foreignkey')
    op.create_foreign_key('rounds_tournament_id_fkey', 'rounds', 'tournament', ['tournament_id'], ['id'])
    op.rename_table('tournaments', 'tournament')
