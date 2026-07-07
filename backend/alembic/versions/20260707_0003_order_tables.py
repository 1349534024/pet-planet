"""add order tables

Revision ID: 20260707_0003
Revises: 20260707_0002
Create Date: 2026-07-07
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260707_0003"
down_revision: str | None = "20260707_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "mall_order",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("order_no", sa.String(length=64), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("address_id", sa.Integer(), nullable=True),
        sa.Column("receiver_name", sa.String(length=64), nullable=False),
        sa.Column("receiver_phone", sa.String(length=32), nullable=False),
        sa.Column("province", sa.String(length=64), nullable=False),
        sa.Column("city", sa.String(length=64), nullable=False),
        sa.Column("district", sa.String(length=64), nullable=False),
        sa.Column("detail", sa.String(length=255), nullable=False),
        sa.Column("total_amount_cent", sa.Integer(), nullable=False),
        sa.Column("freight_amount_cent", sa.Integer(), nullable=False),
        sa.Column("discount_amount_cent", sa.Integer(), nullable=False),
        sa.Column("pay_amount_cent", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("payment_status", sa.String(length=32), nullable=False),
        sa.Column("remark", sa.Text(), nullable=True),
        sa.Column("idempotency_key", sa.String(length=128), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("order_no", name="uq_mall_order_no"),
        sa.UniqueConstraint("user_id", "idempotency_key", name="uq_mall_order_user_idempotency"),
    )
    op.create_index("ix_mall_order_id", "mall_order", ["id"], unique=False)
    op.create_index("ix_mall_order_order_no", "mall_order", ["order_no"], unique=False)
    op.create_index("ix_mall_order_user_id", "mall_order", ["user_id"], unique=False)
    op.create_index("ix_mall_order_address_id", "mall_order", ["address_id"], unique=False)
    op.create_index("ix_mall_order_status", "mall_order", ["status"], unique=False)
    op.create_index("ix_mall_order_payment_status", "mall_order", ["payment_status"], unique=False)
    op.create_index("ix_mall_order_idempotency_key", "mall_order", ["idempotency_key"], unique=False)

    op.create_table(
        "mall_order_item",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("order_id", sa.Integer(), nullable=False),
        sa.Column("order_no", sa.String(length=64), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("sku_id", sa.Integer(), nullable=False),
        sa.Column("merchant_id", sa.Integer(), nullable=True),
        sa.Column("product_title", sa.String(length=255), nullable=False),
        sa.Column("product_main_image", sa.String(length=512), nullable=True),
        sa.Column("sku_name", sa.String(length=128), nullable=False),
        sa.Column("sku_specs", sa.Text(), nullable=True),
        sa.Column("unit_price_cent", sa.Integer(), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("total_amount_cent", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["order_id"], ["mall_order.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_mall_order_item_id", "mall_order_item", ["id"], unique=False)
    op.create_index("ix_mall_order_item_order_id", "mall_order_item", ["order_id"], unique=False)
    op.create_index("ix_mall_order_item_order_no", "mall_order_item", ["order_no"], unique=False)
    op.create_index("ix_mall_order_item_product_id", "mall_order_item", ["product_id"], unique=False)
    op.create_index("ix_mall_order_item_sku_id", "mall_order_item", ["sku_id"], unique=False)
    op.create_index("ix_mall_order_item_merchant_id", "mall_order_item", ["merchant_id"], unique=False)
    op.create_index("ix_mall_order_item_status", "mall_order_item", ["status"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_mall_order_item_status", table_name="mall_order_item")
    op.drop_index("ix_mall_order_item_merchant_id", table_name="mall_order_item")
    op.drop_index("ix_mall_order_item_sku_id", table_name="mall_order_item")
    op.drop_index("ix_mall_order_item_product_id", table_name="mall_order_item")
    op.drop_index("ix_mall_order_item_order_no", table_name="mall_order_item")
    op.drop_index("ix_mall_order_item_order_id", table_name="mall_order_item")
    op.drop_index("ix_mall_order_item_id", table_name="mall_order_item")
    op.drop_table("mall_order_item")

    op.drop_index("ix_mall_order_idempotency_key", table_name="mall_order")
    op.drop_index("ix_mall_order_payment_status", table_name="mall_order")
    op.drop_index("ix_mall_order_status", table_name="mall_order")
    op.drop_index("ix_mall_order_address_id", table_name="mall_order")
    op.drop_index("ix_mall_order_user_id", table_name="mall_order")
    op.drop_index("ix_mall_order_order_no", table_name="mall_order")
    op.drop_index("ix_mall_order_id", table_name="mall_order")
    op.drop_table("mall_order")
