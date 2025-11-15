"""add friendship status and timestamps

Revision ID: 5f9b7f4d3e21
Revises: 42b2fcb0a5a1
Create Date: 2025-11-03 15:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "5f9b7f4d3e21"
down_revision: Union[str, Sequence[str], None] = "42b2fcb0a5a1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "friendships",
        sa.Column("status", sa.String(length=20), nullable=False, server_default="pending"),
    )
    op.add_column(
        "friendships",
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )
    op.add_column(
        "friendships",
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()),
    )
    op.execute(
        "UPDATE friendships SET status='accepted' WHERE accepted_at IS NOT NULL"
    )
    op.drop_column("friendships", "accepted_at")


def downgrade() -> None:
    op.add_column(
        "friendships",
        sa.Column("accepted_at", sa.DateTime(), nullable=True),
    )
    op.execute(
        "UPDATE friendships SET accepted_at=created_at WHERE status='accepted'"
    )
    op.drop_column("friendships", "updated_at")
    op.drop_column("friendships", "created_at")
    op.drop_column("friendships", "status")
