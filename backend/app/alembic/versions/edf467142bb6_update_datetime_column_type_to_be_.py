"""Update datetime column type to be timezone aware


Revision ID: edf467142bb6
Revises: c07b6f5d97f3
Create Date: 2025-02-04 13:11:46.326122

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'edf467142bb6'
down_revision: Union[str, None] = 'c07b6f5d97f3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('transaction', 'timestamp',
               existing_type=postgresql.TIMESTAMP(),
               type_=sa.DateTime(timezone=True),
               nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('transaction', 'timestamp',
               existing_type=sa.DateTime(timezone=True),
               type_=postgresql.TIMESTAMP(),
               nullable=False)
    # ### end Alembic commands ###
