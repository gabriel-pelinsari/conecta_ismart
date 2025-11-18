"""Add gamification and moderation features

Revision ID: 002_add_gamification
Revises: 001_initial_schema
Create Date: 2025-11-18 00:00:00.000000

Adds:
- Points and level fields to user_stats
- point_history table for gamification
- reports table for moderation system
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '002_add_gamification'
down_revision: Union[str, Sequence[str], None] = '001_initial_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # === 1. Add gamification fields to user_stats ===
    op.add_column('user_stats', sa.Column('points', sa.Integer(), server_default='0', nullable=False))
    op.add_column('user_stats', sa.Column('level', sa.String(length=50), server_default='Novato', nullable=False))

    # === 2. Create point_history table ===
    op.create_table(
        'point_history',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('points', sa.Integer(), nullable=False),
        sa.Column('action_type', sa.String(length=50), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('reference_id', sa.Integer(), nullable=True),
        sa.Column('reference_type', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=False), server_default=sa.func.now()),
    )

    # === 3. Create reports table ===
    op.create_table(
        'reports',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('reporter_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('target_type', sa.String(length=20), nullable=False, index=True),
        sa.Column('target_id', sa.Integer(), nullable=False, index=True),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=20), server_default='pending', nullable=False, index=True),
        sa.Column('admin_notes', sa.Text(), nullable=True),
        sa.Column('reviewed_by', sa.Integer(), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('reviewed_at', sa.DateTime(timezone=False), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=False), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=False), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # === 4. Create indexes for better performance ===
    op.create_index('ix_point_history_user_action', 'point_history', ['user_id', 'action_type'])
    op.create_index('ix_reports_target', 'reports', ['target_type', 'target_id'])
    op.create_index('ix_reports_status_created', 'reports', ['status', 'created_at'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_reports_status_created', table_name='reports')
    op.drop_index('ix_reports_target', table_name='reports')
    op.drop_index('ix_point_history_user_action', table_name='point_history')

    # Drop tables
    op.drop_table('reports')
    op.drop_table('point_history')

    # Remove columns from user_stats
    op.drop_column('user_stats', 'level')
    op.drop_column('user_stats', 'points')
