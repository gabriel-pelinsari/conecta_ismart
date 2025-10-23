"""create base schema"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = 'base_init'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create all tables from scratch."""

    op.create_table(
        'users',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('email', sa.String(255), unique=True, nullable=False),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('is_active', sa.Boolean, server_default='true', nullable=False),
        sa.Column('is_admin', sa.Boolean, server_default='false', nullable=False),
        sa.Column('is_verified', sa.Boolean, server_default='false', nullable=False),
        sa.Column('verification_code', sa.String(6), nullable=True),
        sa.Column('role', sa.String(20), server_default='student', nullable=False),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime, server_default=sa.text('now()')),
    )

    op.create_table(
        'profiles',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id', ondelete='CASCADE'), unique=True),
        sa.Column('full_name', sa.String(100), nullable=False),
        sa.Column('nickname', sa.String(50)),
        sa.Column('university', sa.String(100)),
        sa.Column('course', sa.String(100)),
        sa.Column('semester', sa.String(20)),
        sa.Column('photo_url', sa.String(255)),
        sa.Column('linkedin', sa.String(255)),
        sa.Column('instagram', sa.String(255)),
        sa.Column('whatsapp', sa.String(50)),
        sa.Column('show_whatsapp', sa.Boolean, server_default='false', nullable=False),
        sa.Column('is_public', sa.Boolean, server_default='true', nullable=False),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime, server_default=sa.text('now()')),
    )


def downgrade() -> None:
    """Drop all tables."""
    op.drop_table('profiles')
    op.drop_table('users')
