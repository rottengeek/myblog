"""empty message

Revision ID: 838726e5793a
Revises: 3f8562053912
Create Date: 2018-07-25 23:46:38.838814

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '838726e5793a'
down_revision = '3f8562053912'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('avatar_hash', sa.String(length=32), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'avatar_hash')
    # ### end Alembic commands ###