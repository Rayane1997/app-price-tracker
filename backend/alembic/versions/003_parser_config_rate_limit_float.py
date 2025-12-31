"""Set parser_configs.rate_limit_seconds to Float

Revision ID: 003
Revises: 002
Create Date: 2024-01-01 00:10:00.000000
"""
from alembic import op
import sqlalchemy as sa


revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("parser_configs") as batch_op:
        batch_op.alter_column(
            "rate_limit_seconds",
            type_=sa.Float(),
            existing_type=sa.Integer(),
            existing_nullable=True,
        )


def downgrade() -> None:
    with op.batch_alter_table("parser_configs") as batch_op:
        batch_op.alter_column(
            "rate_limit_seconds",
            type_=sa.Integer(),
            existing_type=sa.Float(),
            existing_nullable=True,
        )
