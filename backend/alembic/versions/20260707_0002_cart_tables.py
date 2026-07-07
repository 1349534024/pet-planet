"""add cart tables

Revision ID: 20260707_0002
Revises: 20260706_0001
Create Date: 2026-07-07
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260707_0002"
down_revision: str | None = "20260706_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "cart_item",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("sku_id", sa.Integer(), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("selected", sa.Boolean(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["product_id"], ["product.id"]),
        sa.ForeignKeyConstraint(["sku_id"], ["product_sku.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "sku_id", name="uq_cart_item_user_sku"),
    )
    op.create_index("ix_cart_item_id", "cart_item", ["id"], unique=False)
    op.create_index("ix_cart_item_user_id", "cart_item", ["user_id"], unique=False)
    op.create_index("ix_cart_item_product_id", "cart_item", ["product_id"], unique=False)
    op.create_index("ix_cart_item_sku_id", "cart_item", ["sku_id"], unique=False)
    op.create_index("ix_cart_item_status", "cart_item", ["status"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_cart_item_status", table_name="cart_item")
    op.drop_index("ix_cart_item_sku_id", table_name="cart_item")
    op.drop_index("ix_cart_item_product_id", table_name="cart_item")
    op.drop_index("ix_cart_item_user_id", table_name="cart_item")
    op.drop_index("ix_cart_item_id", table_name="cart_item")
    op.drop_table("cart_item")
