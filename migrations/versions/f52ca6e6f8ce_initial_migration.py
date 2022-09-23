"""Initial Migration

Revision ID: f52ca6e6f8ce
Revises: 
Create Date: 2022-09-17 15:48:37.400088

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f52ca6e6f8ce'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('favorite_color', sa.String(length=120), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'favorite_color')
    # ### end Alembic commands ###