"""Update phone number uniqueness

Revision ID: 450bdebbb5a4
Revises: bfd24b3989d7
Create Date: 2024-12-03 23:39:24.571575

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '450bdebbb5a4'
down_revision: Union[str, None] = 'bfd24b3989d7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('phone_number', sa.VARCHAR(length=11), autoincrement=False, nullable=False),
    sa.Column('otp_code', sa.VARCHAR(length=6), autoincrement=False, nullable=False),
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.PrimaryKeyConstraint('id', name='user_pkey')
    )
    # ### end Alembic commands ###
