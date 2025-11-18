"""Add notifications, events, and mentorship systems

Revision ID: 003_notifications_events
Revises: 002_add_gamification
Create Date: 2025-11-18 06:00:00.000000

Adds:
- notifications table for notification system
- notification_preferences table for user preferences
- events table for event management
- event_participants table for RSVPs
- mentorships table for mentor-mentee relationships
- mentorship_queue table for waiting list
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '003_notifications_events'
down_revision: Union[str, Sequence[str], None] = '002_add_gamification'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # === 1. Create notifications table ===
    op.create_table(
        'notifications',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('notification_type', sa.String(length=50), nullable=False, index=True),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('link', sa.String(length=500), nullable=True),
        sa.Column('is_read', sa.Boolean(), server_default='false', nullable=False, index=True),
        sa.Column('reference_id', sa.Integer(), nullable=True),
        sa.Column('reference_type', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=False), server_default=sa.func.now()),
        sa.Column('read_at', sa.DateTime(timezone=False), nullable=True),
    )

    # === 2. Create notification_preferences table ===
    op.create_table(
        'notification_preferences',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False),
        sa.Column('comment_on_thread', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('friend_request_received', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('friend_request_accepted', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('new_mentee', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('event_reminder', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('badge_earned', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('upvote_received', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('mention', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=False), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=False), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # === 3. Create events table ===
    op.create_table(
        'events',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('event_type', sa.String(length=50), nullable=False, index=True),
        sa.Column('start_datetime', sa.DateTime(timezone=False), nullable=False, index=True),
        sa.Column('end_datetime', sa.DateTime(timezone=False), nullable=False),
        sa.Column('location', sa.String(length=300), nullable=True),
        sa.Column('is_online', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('online_link', sa.String(length=500), nullable=True),
        sa.Column('university', sa.String(length=100), nullable=True, index=True),
        sa.Column('max_participants', sa.Integer(), nullable=True),
        sa.Column('created_by', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('is_cancelled', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('cancelled_reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=False), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=False), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # === 4. Create event_participants table ===
    op.create_table(
        'event_participants',
        sa.Column('event_id', sa.Integer(), sa.ForeignKey('events.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('status', sa.String(length=20), server_default='confirmed', nullable=False),
        sa.Column('attended', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('joined_at', sa.DateTime(timezone=False), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=False), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # === 5. Create mentorships table ===
    op.create_table(
        'mentorships',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('mentor_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('mentee_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('status', sa.String(length=20), server_default='active', nullable=False),
        sa.Column('compatibility_score', sa.Float(), nullable=True),
        sa.Column('matched_at', sa.DateTime(timezone=False), server_default=sa.func.now()),
        sa.Column('completed_at', sa.DateTime(timezone=False), nullable=True),
        sa.Column('cancelled_at', sa.DateTime(timezone=False), nullable=True),
        sa.Column('cancellation_reason', sa.String(length=500), nullable=True),
    )

    # === 6. Create mentorship_queue table ===
    op.create_table(
        'mentorship_queue',
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('requested_at', sa.DateTime(timezone=False), server_default=sa.func.now()),
        sa.Column('priority_score', sa.Float(), server_default='0.0', nullable=False),
    )

    # === 7. Create indexes for better performance ===
    op.create_index('ix_notifications_user_type', 'notifications', ['user_id', 'notification_type'])
    op.create_index('ix_notifications_user_read', 'notifications', ['user_id', 'is_read'])
    op.create_index('ix_events_start_cancelled', 'events', ['start_datetime', 'is_cancelled'])
    op.create_index('ix_event_participants_event_status', 'event_participants', ['event_id', 'status'])
    op.create_index('ix_mentorships_mentor_status', 'mentorships', ['mentor_id', 'status'])
    op.create_index('ix_mentorships_mentee_status', 'mentorships', ['mentee_id', 'status'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_mentorships_mentee_status', table_name='mentorships')
    op.drop_index('ix_mentorships_mentor_status', table_name='mentorships')
    op.drop_index('ix_event_participants_event_status', table_name='event_participants')
    op.drop_index('ix_events_start_cancelled', table_name='events')
    op.drop_index('ix_notifications_user_read', table_name='notifications')
    op.drop_index('ix_notifications_user_type', table_name='notifications')

    # Drop tables
    op.drop_table('mentorship_queue')
    op.drop_table('mentorships')
    op.drop_table('event_participants')
    op.drop_table('events')
    op.drop_table('notification_preferences')
    op.drop_table('notifications')
