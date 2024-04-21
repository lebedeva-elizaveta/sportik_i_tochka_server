"""update activity fields

Revision ID: ee5d7e5c0787
Revises: a0a595399b12
Create Date: 2024-04-21 15:12:35.609831

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'ee5d7e5c0787'
down_revision = 'a0a595399b12'
branch_labels = None
depends_on = None


from alembic import op
import sqlalchemy as sa

def upgrade():
    # Переименование столбца в таблице activity
    op.alter_column('activity', 'speed', new_column_name='avg_speed')
    op.alter_column('activity', 'type', new_column_name='activity_type')


def downgrade():
    # Возврат изменения
    op.alter_column('activity', 'avg_speed', new_column_name='speed')
    op.alter_column('activity', 'activity_type', new_column_name='type')
