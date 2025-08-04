"""Fix initial ratings to 1000

Revision ID: fix_initial_ratings
Revises: 908cf7ecefe9
Create Date: 2025-08-04

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fix_initial_ratings'
down_revision = '908cf7ecefe9'
branch_labels = None
depends_on = None


def upgrade():
    # Update any ratings that are exactly 1500 (the old default) to 1000
    op.execute("""
        UPDATE player_ratings 
        SET current_rating = 1000.0,
            peak_rating = CASE 
                WHEN peak_rating = 1500.0 THEN 1000.0 
                ELSE peak_rating - 500.0 
            END,
            lowest_rating = CASE 
                WHEN lowest_rating = 1500.0 THEN 1000.0 
                ELSE lowest_rating - 500.0 
            END
        WHERE current_rating = 1500.0
    """)
    
    # Adjust all ratings down by 500 to match new 1000 base
    op.execute("""
        UPDATE player_ratings 
        SET current_rating = current_rating - 500.0,
            peak_rating = peak_rating - 500.0,
            lowest_rating = lowest_rating - 500.0
        WHERE current_rating != 1000.0
    """)
    
    # Update rating history
    op.execute("""
        UPDATE rating_history 
        SET old_rating = old_rating - 500.0,
            new_rating = new_rating - 500.0,
            rating_change = new_rating - old_rating
    """)


def downgrade():
    # Revert ratings back to 1500 base
    op.execute("""
        UPDATE player_ratings 
        SET current_rating = current_rating + 500.0,
            peak_rating = peak_rating + 500.0,
            lowest_rating = lowest_rating + 500.0
    """)
    
    op.execute("""
        UPDATE rating_history 
        SET old_rating = old_rating + 500.0,
            new_rating = new_rating + 500.0,
            rating_change = new_rating - old_rating
    """)