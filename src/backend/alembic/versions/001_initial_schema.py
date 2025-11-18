"""Initial schema creation - all tables

Revision ID: 001_initial_schema
Revises:
Create Date: 2025-11-17 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '001_initial_schema'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # === TABLE: users ===
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('email', sa.String(length=255), unique=True, nullable=False, index=True),
        sa.Column('hashed_password', sa.String(length=255), nullable=True),  # nullable for pending users
        sa.Column('is_active', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('is_admin', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('is_verified', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=False), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=False), server_default=sa.func.now()),
    )

    # === TABLE: user_stats ===
    op.create_table(
        'user_stats',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False),
        sa.Column('total_posts', sa.Integer(), server_default='0'),
        sa.Column('total_comments', sa.Integer(), server_default='0'),
        sa.Column('total_votes_received', sa.Integer(), server_default='0'),
        sa.Column('total_friendships', sa.Integer(), server_default='0'),
        sa.Column('badges_count', sa.Integer(), server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=False), server_default=sa.func.now()),
    )

    # === TABLE: profiles ===
    op.create_table(
        'profiles',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False),
        sa.Column('full_name', sa.String(length=100), nullable=False),
        sa.Column('nickname', sa.String(length=50)),
        sa.Column('university', sa.String(length=100)),
        sa.Column('course', sa.String(length=100)),
        sa.Column('semester', sa.String(length=20)),
        sa.Column('bio', sa.Text()),
        sa.Column('photo_url', sa.String(length=255)),
        sa.Column('linkedin', sa.String(length=255)),
        sa.Column('instagram', sa.String(length=255)),
        sa.Column('whatsapp', sa.String(length=50)),
        sa.Column('show_whatsapp', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('is_public', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=False), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=False), server_default=sa.func.now()),
    )

    # === TABLE: interests ===
    op.create_table(
        'interests',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('name', sa.String(length=100), unique=True, nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('icon_url', sa.String(length=255)),
    )

    # === TABLE: user_interests (junction table) ===
    op.create_table(
        'user_interests',
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('interest_id', sa.Integer(), sa.ForeignKey('interests.id', ondelete='CASCADE'), primary_key=True),
    )

    # === TABLE: friendships ===
    op.create_table(
        'friendships',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('friend_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('status', sa.String(length=20), server_default='pending', nullable=False),  # pending, accepted, blocked
        sa.Column('created_at', sa.DateTime(timezone=False), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=False), server_default=sa.func.now()),
        sa.UniqueConstraint('user_id', 'friend_id', name='unique_friendship_pair'),
    )

    # === TABLE: university_groups ===
    op.create_table(
        'university_groups',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('name', sa.String(length=255), unique=True, nullable=False),
        sa.Column('university', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('created_at', sa.DateTime(timezone=False), server_default=sa.func.now()),
    )

    # === TABLE: university_group_members ===
    op.create_table(
        'university_group_members',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('group_id', sa.Integer(), sa.ForeignKey('university_groups.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('joined_at', sa.DateTime(timezone=False), server_default=sa.func.now()),
        sa.UniqueConstraint('group_id', 'user_id', name='unique_group_member'),
    )

    # === TABLE: badges ===
    op.create_table(
        'badges',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('icon_url', sa.String(length=255)),
        sa.Column('created_at', sa.DateTime(timezone=False), server_default=sa.func.now()),
    )

    # === TABLE: user_badges ===
    op.create_table(
        'user_badges',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('badge_id', sa.Integer(), sa.ForeignKey('badges.id', ondelete='CASCADE'), nullable=False),
        sa.Column('earned_at', sa.DateTime(timezone=False), server_default=sa.func.now()),
        sa.UniqueConstraint('user_id', 'badge_id', name='unique_user_badge'),
    )

    # === TABLE: threads ===
    op.create_table(
        'threads',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('title', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),  # 'geral' or 'faculdade'
        sa.Column('tags', sa.String(length=200), server_default=''),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('university', sa.String(length=100)),
        sa.Column('is_reported', sa.Boolean(), server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=False), server_default=sa.func.now()),
    )

    # === TABLE: comments ===
    op.create_table(
        'comments',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('thread_id', sa.Integer(), sa.ForeignKey('threads.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=False), server_default=sa.func.now()),
    )

    # === TABLE: thread_votes ===
    op.create_table(
        'thread_votes',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('thread_id', sa.Integer(), sa.ForeignKey('threads.id', ondelete='CASCADE'), nullable=False),
        sa.Column('value', sa.Integer()),  # +1 or -1
        sa.UniqueConstraint('user_id', 'thread_id', name='unique_user_thread_vote'),
    )

    # === TABLE: comment_votes ===
    op.create_table(
        'comment_votes',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('comment_id', sa.Integer(), sa.ForeignKey('comments.id', ondelete='CASCADE'), nullable=False),
        sa.Column('value', sa.Integer()),  # +1 or -1
        sa.UniqueConstraint('user_id', 'comment_id', name='unique_user_comment_vote'),
    )


def downgrade() -> None:
    op.drop_table('comment_votes')
    op.drop_table('thread_votes')
    op.drop_table('comments')
    op.drop_table('threads')
    op.drop_table('user_badges')
    op.drop_table('badges')
    op.drop_table('university_group_members')
    op.drop_table('university_groups')
    op.drop_table('friendships')
    op.drop_table('user_interests')
    op.drop_table('interests')
    op.drop_table('profiles')
    op.drop_table('user_stats')
    op.drop_table('users')
