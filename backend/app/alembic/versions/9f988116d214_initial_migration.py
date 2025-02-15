"""Initial migration

Revision ID: 9f988116d214
Revises: 
Create Date: 2025-02-04 00:08:37.862816

"""
from typing import Sequence, Union
import sqlmodel.sql.sqltypes

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9f988116d214'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('lastupdate',
    sa.Column('type', sqlmodel.sql.sqltypes.AutoString(length=50), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_lastupdate_type'), 'lastupdate', ['type'], unique=True)
    op.create_table('spotprice',
    sa.Column('symbol', sqlmodel.sql.sqltypes.AutoString(length=10), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=False),
    sa.Column('price', sa.Float(), nullable=False),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_spotprice_symbol'), 'spotprice', ['symbol'], unique=False)
    op.create_index(op.f('ix_spotprice_timestamp'), 'spotprice', ['timestamp'], unique=False)
    op.create_table('transaction',
    sa.Column('tx_hash', sqlmodel.sql.sqltypes.AutoString(length=66), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=False),
    sa.Column('txn_fee_usdt', sa.Float(), nullable=False),
    sa.Column('gas_used', sa.Integer(), nullable=False),
    sa.Column('gas_price_wei', sa.Integer(), nullable=False),
    sa.Column('txn_fee_eth', sa.Float(), nullable=False),
    sa.Column('eth_usdt_price', sa.Float(), nullable=False),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_transaction_timestamp'), 'transaction', ['timestamp'], unique=False)
    op.create_index(op.f('ix_transaction_tx_hash'), 'transaction', ['tx_hash'], unique=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_transaction_tx_hash'), table_name='transaction')
    op.drop_index(op.f('ix_transaction_timestamp'), table_name='transaction')
    op.drop_table('transaction')
    op.drop_index(op.f('ix_spotprice_timestamp'), table_name='spotprice')
    op.drop_index(op.f('ix_spotprice_symbol'), table_name='spotprice')
    op.drop_table('spotprice')
    op.drop_index(op.f('ix_lastupdate_type'), table_name='lastupdate')
    op.drop_table('lastupdate')
    # ### end Alembic commands ###
