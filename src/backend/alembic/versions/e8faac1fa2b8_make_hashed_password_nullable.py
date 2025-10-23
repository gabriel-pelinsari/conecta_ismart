"""make hashed_password nullable

Revision ID: e8faac1fa2b8
Revises: 5f8cef47c194
Create Date: 2025-10-23 10:08:05.574099

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e8faac1fa2b8'
down_revision: Union[str, Sequence[str], None] = '5f8cef47c194'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.alter_column('users', 'hashed_password',
                    existing_type=sa.String(255),
                    nullable=True)  # <-- permitir NULL

def downgrade():
    op.alter_column('users', 'hashed_password',
                    existing_type=sa.String(255),
                    nullable=False)