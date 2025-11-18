"""Add verification code column to users

Revision ID: 005_add_verification_code
Revises: 004_add_polls
Create Date: 2025-11-19 15:30:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "005_add_verification_code"
down_revision: Union[str, Sequence[str], None] = "004_add_polls"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("verification_code", sa.String(length=6), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("users", "verification_code")
