"""Fix user tables mistakes

Revision ID: bfd24b3989d7
Revises: 888f3ec5b5ea
Create Date: 2024-12-03 23:34:34.501676

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bfd24b3989d7'
down_revision: Union[str, None] = '888f3ec5b5ea'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
