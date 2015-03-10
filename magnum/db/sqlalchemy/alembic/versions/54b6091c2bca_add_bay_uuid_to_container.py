"""Add bay_uuid to container

Revision ID: 54b6091c2bca
Revises: 1afee1db6cd0
Create Date: 2015-03-10 17:25:41.685392

"""

# revision identifiers, used by Alembic.
revision = '54b6091c2bca'
down_revision = '1afee1db6cd0'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    op.add_column('container', sa.Column('bay_uuid', sa.String(length=36), nullable=True))


def downgrade():
    op.drop_column('container', 'bay_uuid')
