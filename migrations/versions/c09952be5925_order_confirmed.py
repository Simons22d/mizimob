"""order confirmed 

Revision ID: c09952be5925
Revises: 7793ad9963a9
Create Date: 2021-01-28 05:40:44.138861

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c09952be5925'
down_revision = '7793ad9963a9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('order', sa.Column('confirmed', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('order', 'confirmed')
    # ### end Alembic commands ###
