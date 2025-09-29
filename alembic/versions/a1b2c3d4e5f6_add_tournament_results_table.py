"""add tournament results table

Revision ID: a1b2c3d4e5f6
Revises: 72267b10abcf
Create Date: 2025-09-28 15:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '72267b10abcf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create tournament_results table
    op.create_table('tournament_results',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('tournament_id', sa.String(), nullable=False),
        sa.Column('player_id', sa.String(), nullable=False),
        sa.Column('final_position', sa.Integer(), nullable=False),
        sa.Column('total_score', sa.Integer(), nullable=False),
        sa.Column('points_difference', sa.Integer(), nullable=True, default=0),
        sa.Column('matches_played', sa.Integer(), nullable=True, default=0),
        sa.Column('matches_won', sa.Integer(), nullable=True, default=0),
        sa.Column('matches_lost', sa.Integer(), nullable=True, default=0),
        sa.Column('matches_tied', sa.Integer(), nullable=True, default=0),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['player_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['tournament_id'], ['tournaments.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tournament_id', 'player_id', name='unique_tournament_player_result')
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Drop tournament_results table
    op.drop_table('tournament_results')
