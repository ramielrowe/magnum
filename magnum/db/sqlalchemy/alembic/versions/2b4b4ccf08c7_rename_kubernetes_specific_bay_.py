"""Rename-kubernetes-specific-bay-attributes

Revision ID: 2b4b4ccf08c7
Revises: 2d1354bbf76e
Create Date: 2015-03-24 16:04:53.848780

"""

# revision identifiers, used by Alembic.
revision = '2b4b4ccf08c7'
down_revision = '2d1354bbf76e'

from magnum.db.sqlalchemy import models

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


def upgrade():
    op.alter_column('bay', 'master_address',
                    new_column_name='api_address',
                    existing_type=sa.String(255))
    op.alter_column('bay', 'minions_address',
                    new_column_name='node_addresses',
                    existing_type=models.JSONEncodedList)


def downgrade():
    op.alter_column('bay', 'api_address',
                    new_column_name='master_address',
                    existing_type=models.JSONEncodedList)
    op.alter_column('bay', 'node_addresses',
                    new_column_name='minions_address',
                    existing_type=sa.String(255))
