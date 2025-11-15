"""allow null hashed_password for pending users

Revision ID: 42b2fcb0a5a1
Revises: 277ec18ea436
Create Date: 2025-11-03 14:20:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "42b2fcb0a5a1"
down_revision: Union[str, Sequence[str], None] = "277ec18ea436"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "users",
        "hashed_password",
        existing_type=sa.String(length=255),
        nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        "users",
        "hashed_password",
        existing_type=sa.String(length=255),
        nullable=False,
    )
