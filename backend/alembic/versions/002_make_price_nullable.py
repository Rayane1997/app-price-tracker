"""Make price column nullable

Revision ID: 002
Revises: 001
Create Date: 2025-12-29 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Make price column nullable to handle failed scraping attempts
    op.alter_column('price_history', 'price',
                    existing_type=sa.Float(),
                    nullable=True)


def downgrade() -> None:
    # Revert price column back to NOT NULL
    op.alter_column('price_history', 'price',
                    existing_type=sa.Float(),
                    nullable=False)
