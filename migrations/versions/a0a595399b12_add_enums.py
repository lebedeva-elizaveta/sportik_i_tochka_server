"""add enums

Revision ID: a0a595399b12
Revises: 8fcaf160114b
Create Date: 2024-04-21 12:49:59.272791

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'a0a595399b12'
down_revision = '8fcaf160114b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user_model')
    with op.batch_alter_table('achievement', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_achievement_user_id'), ['user_id'], unique=False)

    with op.batch_alter_table('activity', schema=None) as batch_op:
        batch_op.alter_column('type',
               existing_type=sa.VARCHAR(),
               type_=sa.Enum('RUNNING', 'SWIMMING', 'CYCLING', name='activitytype'),
               existing_nullable=False)
        batch_op.create_index(batch_op.f('ix_activity_user_id'), ['user_id'], unique=False)

    with op.batch_alter_table('admin__premium', schema=None) as batch_op:
        batch_op.alter_column('action',
               existing_type=sa.VARCHAR(length=255),
               type_=sa.Enum('GRANT_PREMIUM', 'REVOKE_PREMIUM', name='adminpremiumaction'),
               existing_nullable=False)

    with op.batch_alter_table('admin__user', schema=None) as batch_op:
        batch_op.alter_column('action',
               existing_type=sa.VARCHAR(length=255),
               type_=sa.Enum('BLOCK', 'UNBLOCK', name='adminuseraction'),
               existing_nullable=False)

    with op.batch_alter_table('premium', schema=None) as batch_op:
        batch_op.alter_column('start_date',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True)
        batch_op.alter_column('end_date',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True)
        batch_op.create_index(batch_op.f('ix_premium_user_id'), ['user_id'], unique=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('premium', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_premium_user_id'))
        batch_op.alter_column('end_date',
               existing_type=postgresql.TIMESTAMP(),
               nullable=False)
        batch_op.alter_column('start_date',
               existing_type=postgresql.TIMESTAMP(),
               nullable=False)

    with op.batch_alter_table('admin__user', schema=None) as batch_op:
        batch_op.alter_column('action',
               existing_type=sa.Enum('BLOCK', 'UNBLOCK', name='adminuseraction'),
               type_=sa.VARCHAR(length=255),
               existing_nullable=False)

    with op.batch_alter_table('admin__premium', schema=None) as batch_op:
        batch_op.alter_column('action',
               existing_type=sa.Enum('GRANT_PREMIUM', 'REVOKE_PREMIUM', name='adminpremiumaction'),
               type_=sa.VARCHAR(length=255),
               existing_nullable=False)

    with op.batch_alter_table('activity', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_activity_user_id'))
        batch_op.alter_column('type',
               existing_type=sa.Enum('RUNNING', 'SWIMMING', 'CYCLING', name='activitytype'),
               type_=sa.VARCHAR(),
               existing_nullable=False)

    with op.batch_alter_table('achievement', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_achievement_user_id'))

    op.create_table('user_model',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('email', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.Column('password_hash', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.Column('name', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.Column('birthday', sa.DATE(), autoincrement=False, nullable=False),
    sa.Column('phone', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.Column('weight', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('avatar', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('date_of_registration', sa.DATE(), autoincrement=False, nullable=True),
    sa.Column('is_blocked', sa.BOOLEAN(), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id', name='user_model_pkey')
    )
    # ### end Alembic commands ###
