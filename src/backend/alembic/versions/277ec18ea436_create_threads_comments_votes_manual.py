"""create threads/comments/votes (manual)

Revision ID: 277ec18ea436
Revises: 
Create Date: 2025-10-24 19:33:40.419988

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '277ec18ea436'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'threads',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('title', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('tags', sa.String(length=200), default=""),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('university', sa.String(length=100)),
        sa.Column('is_reported', sa.Boolean(), default=False),
    )

    op.create_table(
        'comments',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('thread_id', sa.Integer(), sa.ForeignKey('threads.id'), nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
    )

    op.create_table(
        'thread_votes',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id')),
        sa.Column('thread_id', sa.Integer(), sa.ForeignKey('threads.id')),
        sa.Column('value', sa.Integer()),
        sa.UniqueConstraint('user_id', 'thread_id', name='unique_user_thread_vote')
    )

    op.create_table(
        'comment_votes',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id')),
        sa.Column('comment_id', sa.Integer(), sa.ForeignKey('comments.id')),
        sa.Column('value', sa.Integer()),
        sa.UniqueConstraint('user_id', 'comment_id', name='unique_user_comment_vote')
    )


def downgrade() -> None:
    op.drop_table('comment_votes')
    op.drop_table('thread_votes')
    op.drop_table('comments')
    op.drop_table('threads')