"""update note column character limit

Revision ID: ea252a0674f7
Revises: c0abedaecc75
Create Date: 2023-04-13 14:56:27.501070

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ea252a0674f7'
down_revision = 'c0abedaecc75'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(table_name='ApproverRequestHistory', column_name='note', type_=sa.String(length=100))

def downgrade():
    op.alter_column(table_name='ApproverRequestHistory', column_name='note', type_=sa.String(length=50))

