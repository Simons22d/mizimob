"""order number 

Revision ID: b1f3462e4a07
Revises: c09952be5925
Create Date: 2021-01-29 05:45:34.519301

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b1f3462e4a07'
down_revision = 'c09952be5925'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('order_group',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('products', sa.String(length=255), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('order_number', sa.String(length=255), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('order_number')
    )
    op.add_column('order', sa.Column('unique_code', sa.String(length=255), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('order', 'unique_code')
    op.drop_table('order_group')
    # ### end Alembic commands ###
