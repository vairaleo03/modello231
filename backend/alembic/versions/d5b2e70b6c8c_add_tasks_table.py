"""add tasks table

Revision ID: d5b2e70b6c8c
Revises: 7ffbd67a101a
Create Date: 2025-05-06 06:58:27.205100

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd5b2e70b6c8c'
down_revision: Union[str, None] = '7ffbd67a101a'
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
