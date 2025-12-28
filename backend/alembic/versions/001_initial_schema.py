"""Initial schema

Revision ID: 001
Revises:
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Create products table
    op.create_table(
        'products',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=500), nullable=False),
        sa.Column('url', sa.Text(), nullable=False),
        sa.Column('domain', sa.String(length=255), nullable=False),
        sa.Column('current_price', sa.Float(), nullable=True),
        sa.Column('currency', sa.String(length=3), nullable=True),
        sa.Column('target_price', sa.Float(), nullable=True),
        sa.Column('image_url', sa.Text(), nullable=True),
        sa.Column('check_frequency_hours', sa.Integer(), nullable=True),
        sa.Column('status', sa.Enum('ACTIVE', 'ERROR', 'NOT_TRACKABLE', 'PAUSED', name='productstatus'), nullable=True),
        sa.Column('tags', sa.String(length=500), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('last_checked_at', sa.DateTime(), nullable=True),
        sa.Column('last_success_at', sa.DateTime(), nullable=True),
        sa.Column('consecutive_errors', sa.Integer(), nullable=True),
        sa.Column('last_error_message', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_products_id'), 'products', ['id'], unique=False)
    op.create_index(op.f('ix_products_domain'), 'products', ['domain'], unique=False)
    op.create_index(op.f('ix_products_status'), 'products', ['status'], unique=False)

    # Create price_history table
    op.create_table(
        'price_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('price', sa.Float(), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=True),
        sa.Column('is_promo', sa.Boolean(), nullable=True),
        sa.Column('promo_percentage', sa.Float(), nullable=True),
        sa.Column('source', sa.String(length=50), nullable=True),
        sa.Column('scrape_duration_ms', sa.Integer(), nullable=True),
        sa.Column('recorded_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_price_history_id'), 'price_history', ['id'], unique=False)
    op.create_index(op.f('ix_price_history_product_id'), 'price_history', ['product_id'], unique=False)
    op.create_index(op.f('ix_price_history_recorded_at'), 'price_history', ['recorded_at'], unique=False)

    # Create alerts table
    op.create_table(
        'alerts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('type', sa.Enum('PRICE_DROP', 'TARGET_REACHED', 'PROMO_DETECTED', name='alerttype'), nullable=False),
        sa.Column('status', sa.Enum('UNREAD', 'READ', 'DISMISSED', name='alertstatus'), nullable=True),
        sa.Column('old_price', sa.Float(), nullable=True),
        sa.Column('new_price', sa.Float(), nullable=False),
        sa.Column('price_drop_percentage', sa.Float(), nullable=True),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('read_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_alerts_id'), 'alerts', ['id'], unique=False)
    op.create_index(op.f('ix_alerts_product_id'), 'alerts', ['product_id'], unique=False)
    op.create_index(op.f('ix_alerts_status'), 'alerts', ['status'], unique=False)
    op.create_index(op.f('ix_alerts_created_at'), 'alerts', ['created_at'], unique=False)

    # Create parser_configs table
    op.create_table(
        'parser_configs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('domain', sa.String(length=255), nullable=False),
        sa.Column('domain_pattern', sa.String(length=500), nullable=True),
        sa.Column('requires_javascript', sa.Boolean(), nullable=True),
        sa.Column('use_playwright', sa.Boolean(), nullable=True),
        sa.Column('price_selectors', sa.JSON(), nullable=False),
        sa.Column('name_selectors', sa.JSON(), nullable=True),
        sa.Column('image_selectors', sa.JSON(), nullable=True),
        sa.Column('rate_limit_seconds', sa.Integer(), nullable=True),
        sa.Column('max_retries', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('error_count', sa.Integer(), nullable=True),
        sa.Column('last_error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('last_used_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_parser_configs_id'), 'parser_configs', ['id'], unique=False)
    op.create_index(op.f('ix_parser_configs_domain'), 'parser_configs', ['domain'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_parser_configs_domain'), table_name='parser_configs')
    op.drop_index(op.f('ix_parser_configs_id'), table_name='parser_configs')
    op.drop_table('parser_configs')

    op.drop_index(op.f('ix_alerts_created_at'), table_name='alerts')
    op.drop_index(op.f('ix_alerts_status'), table_name='alerts')
    op.drop_index(op.f('ix_alerts_product_id'), table_name='alerts')
    op.drop_index(op.f('ix_alerts_id'), table_name='alerts')
    op.drop_table('alerts')

    op.drop_index(op.f('ix_price_history_recorded_at'), table_name='price_history')
    op.drop_index(op.f('ix_price_history_product_id'), table_name='price_history')
    op.drop_index(op.f('ix_price_history_id'), table_name='price_history')
    op.drop_table('price_history')

    op.drop_index(op.f('ix_products_status'), table_name='products')
    op.drop_index(op.f('ix_products_domain'), table_name='products')
    op.drop_index(op.f('ix_products_id'), table_name='products')
    op.drop_table('products')
