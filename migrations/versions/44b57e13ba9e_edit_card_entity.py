"""edit card entity

Revision ID: 44b57e13ba9e
Revises: 99e20ed60218
Create Date: 2024-04-21 21:29:27.104672

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '44b57e13ba9e'
down_revision = '99e20ed60218'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('card', 'card_number_hash', new_column_name='card_number')
    op.alter_column('card', 'month_hash', new_column_name='month')
    op.alter_column('card', 'year_hash', new_column_name='year')
    op.alter_column('card', 'cvv_hash', new_column_name='cvv')


def downgrade():
    op.alter_column('card', 'card_number', new_column_name='card_number_hash')
    op.alter_column('card', 'month', new_column_name='month_hash')
    op.alter_column('card', 'year', new_column_name='year_hash')
    op.alter_column('card', 'cvv', new_column_name='cvv_hash')
