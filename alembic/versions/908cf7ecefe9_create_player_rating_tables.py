"""create_player_rating_tables

Revision ID: 908cf7ecefe9
Revises: f721ad6d988b
Create Date: 2025-08-02 15:29:21.512309

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '908cf7ecefe9'
down_revision: Union[str, None] = 'f721ad6d988b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create player_ratings table
    op.create_table('player_ratings',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('current_rating', sa.Float(), nullable=False),
        sa.Column('peak_rating', sa.Float(), nullable=False),
        sa.Column('lowest_rating', sa.Float(), nullable=False),
        sa.Column('matches_played', sa.Integer(), nullable=False),
        sa.Column('matches_won', sa.Integer(), nullable=False),
        sa.Column('total_points_scored', sa.Integer(), nullable=False),
        sa.Column('total_points_possible', sa.Integer(), nullable=False),
        sa.Column('tournaments_played', sa.Integer(), nullable=False),
        sa.Column('first_place_finishes', sa.Integer(), nullable=False),
        sa.Column('second_place_finishes', sa.Integer(), nullable=False),
        sa.Column('third_place_finishes', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    
    # Create rating_history table
    op.create_table('rating_history',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('player_rating_id', sa.String(), nullable=False),
        sa.Column('tournament_id', sa.String(), nullable=True),
        sa.Column('match_id', sa.String(), nullable=True),
        sa.Column('old_rating', sa.Float(), nullable=False),
        sa.Column('new_rating', sa.Float(), nullable=False),
        sa.Column('rating_change', sa.Float(), nullable=False),
        sa.Column('opponent_ratings', sa.Text(), nullable=True),
        sa.Column('match_result', sa.String(), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['player_rating_id'], ['player_ratings.id'], ),
        sa.ForeignKeyConstraint(['tournament_id'], ['tournaments.id'], ),
        sa.ForeignKeyConstraint(['match_id'], ['rounds.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('rating_history')
    op.drop_table('player_ratings')
