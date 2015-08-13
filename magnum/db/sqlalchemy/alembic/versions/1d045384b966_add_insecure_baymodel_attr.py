"""add-insecure-baymodel-attr

Revision ID: 1d045384b966
Revises: 1481f5b560dd
Create Date: 2015-09-23 18:17:10.195121

"""

# revision identifiers, used by Alembic.
revision = '1d045384b966'
down_revision = '1481f5b560dd'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    op.add_column('baymodel', sa.Column('insecure', sa.Boolean(), nullable=True))
