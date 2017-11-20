"""empty message

Revision ID: 5abb08e2b21f
Revises: 4a5788277a99
Create Date: 2017-11-20 14:03:41.061735

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '5abb08e2b21f'
down_revision = '4a5788277a99'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('posts', schema=None) as batch_op:
        batch_op.add_column(sa.Column('disabled', sa.Boolean(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('posts', schema=None) as batch_op:
        batch_op.drop_column('disabled')

    # ### end Alembic commands ###
