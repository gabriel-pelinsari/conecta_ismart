"""add bio to profiles

Revision ID: 5f8cef47c194
Revises: 46a37f42e24b
Create Date: 2025-10-23 09:45:58.123141

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5f8cef47c194'
down_revision: Union[str, Sequence[str], None] = '46a37f42e24b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column('profiles', sa.Column('bio', sa.Text(), nullable=True))

def downgrade():
    op.drop_column('profiles', 'bio')