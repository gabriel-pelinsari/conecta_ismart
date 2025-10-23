"""add social features"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# Revision identifiers
revision: str = 'add_social_features'
down_revision: Union[str, Sequence[str], None] = 'base_init'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add social and gamification tables."""

    # --- Interests ---
    op.create_table(
        'interests',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(80), unique=True, nullable=False)
    )

    op.create_table(
        'user_interests',
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('interest_id', sa.Integer, sa.ForeignKey('interests.id', ondelete='CASCADE'), primary_key=True)
    )

    # --- Badges ---
    op.create_table(
        'badges',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('code', sa.String(64), unique=True, nullable=False),
        sa.Column('name', sa.String(120), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('icon', sa.String(255))
    )

    op.create_table(
        'user_badges',
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('badge_id', sa.Integer, sa.ForeignKey('badges.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('awarded_at', sa.DateTime, server_default=sa.text('now()'))
    )

    # --- Friendships ---
    op.create_table(
        'friendships',
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('friend_id', sa.Integer, sa.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('accepted_at', sa.DateTime)
    )

    # --- User Stats ---
    op.create_table(
        'user_stats',
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('threads_count', sa.Integer, server_default='0'),
        sa.Column('comments_count', sa.Integer, server_default='0'),
        sa.Column('events_count', sa.Integer, server_default='0')
    )


def downgrade() -> None:
    """Remove social and gamification tables."""
    op.drop_table('user_stats')
    op.drop_table('friendships')
    op.drop_table('user_badges')
    op.drop_table('badges')
    op.drop_table('user_interests')
    op.drop_table('interests')
