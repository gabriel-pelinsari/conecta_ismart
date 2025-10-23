"""merge multiple heads"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'd79d6778b82e'
down_revision: Union[str, Sequence[str], None] = ('add_social_features', '408cc10e106c')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    pass

def downgrade() -> None:
    pass
