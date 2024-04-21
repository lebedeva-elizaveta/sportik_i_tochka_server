"""update activity fields_2

Revision ID: 99e20ed60218
Revises: ee5d7e5c0787
Create Date: 2024-04-21 15:20:41.647776

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '99e20ed60218'
down_revision = 'ee5d7e5c0787'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('activity', 'calories', new_column_name='calories_burned')
    op.alter_column('activity', 'distance', new_column_name='distance_in_meters')


def downgrade():
    op.alter_column('activity', 'calories_burned', new_column_name='calories')
    op.alter_column('activity', 'distance_in_meters', new_column_name='distance')