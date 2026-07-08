"""add product catalog tables

Revision ID: 20260706_0001
Revises: 5842f5236297
Create Date: 2026-07-06
"""

from collections.abc import Sequence
from datetime import datetime, timezone

import sqlalchemy as sa
from alembic import op

revision: str = "20260706_0001"
down_revision: str | None = "5842f5236297"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _timestamps() -> dict[str, datetime | None]:
    now = datetime.now(timezone.utc)
    return {"created_at": now, "updated_at": now, "deleted_at": None}


def upgrade() -> None:
    op.create_table(
        "product_category",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("parent_id", sa.Integer(), nullable=True),
        sa.Column("name", sa.String(length=64), nullable=False),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column("icon_url", sa.String(length=512), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["parent_id"], ["product_category.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code", name="uq_product_category_code"),
    )
    op.create_index("ix_product_category_pk", "product_category", ["id"], unique=False)
    op.create_index("ix_product_category_parent_id", "product_category", ["parent_id"], unique=False)
    op.create_index("ix_product_category_name", "product_category", ["name"], unique=False)
    op.create_index("ix_product_category_code", "product_category", ["code"], unique=False)
    op.create_index("ix_product_category_status", "product_category", ["status"], unique=False)

    op.create_table(
        "brand",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("logo_url", sa.String(length=512), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_brand_pk", "brand", ["id"], unique=False)
    op.create_index("ix_brand_name", "brand", ["name"], unique=True)
    op.create_index("ix_brand_status", "brand", ["status"], unique=False)

    op.create_table(
        "product",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("merchant_id", sa.Integer(), nullable=True),
        sa.Column("category_id", sa.Integer(), nullable=False),
        sa.Column("brand_id", sa.Integer(), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("subtitle", sa.String(length=255), nullable=True),
        sa.Column("main_image", sa.String(length=512), nullable=True),
        sa.Column("images", sa.Text(), nullable=True),
        sa.Column("video_url", sa.String(length=512), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("detail_html", sa.Text(), nullable=True),
        sa.Column("price_cent", sa.Integer(), nullable=False),
        sa.Column("original_price_cent", sa.Integer(), nullable=True),
        sa.Column("sales_count", sa.Integer(), nullable=False),
        sa.Column("review_count", sa.Integer(), nullable=False),
        sa.Column("rating", sa.Integer(), nullable=False),
        sa.Column("applicable_pet", sa.String(length=128), nullable=True),
        sa.Column("applicable_age", sa.String(length=128), nullable=True),
        sa.Column("origin_place", sa.String(length=128), nullable=True),
        sa.Column("shelf_life", sa.String(length=128), nullable=True),
        sa.Column("ingredients", sa.Text(), nullable=True),
        sa.Column("usage_instructions", sa.Text(), nullable=True),
        sa.Column("notice", sa.Text(), nullable=True),
        sa.Column("shipping_note", sa.Text(), nullable=True),
        sa.Column("after_sale_policy", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["brand_id"], ["brand.id"]),
        sa.ForeignKeyConstraint(["category_id"], ["product_category.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_product_pk", "product", ["id"], unique=False)
    op.create_index("ix_product_merchant_id", "product", ["merchant_id"], unique=False)
    op.create_index("ix_product_category_fk", "product", ["category_id"], unique=False)
    op.create_index("ix_product_brand_fk", "product", ["brand_id"], unique=False)
    op.create_index("ix_product_title", "product", ["title"], unique=False)
    op.create_index("ix_product_price_cent", "product", ["price_cent"], unique=False)
    op.create_index("ix_product_sales_count", "product", ["sales_count"], unique=False)
    op.create_index("ix_product_status", "product", ["status"], unique=False)

    op.create_table(
        "product_sku",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("sku_code", sa.String(length=64), nullable=False),
        sa.Column("sku_name", sa.String(length=128), nullable=False),
        sa.Column("specs", sa.Text(), nullable=True),
        sa.Column("price_cent", sa.Integer(), nullable=False),
        sa.Column("original_price_cent", sa.Integer(), nullable=True),
        sa.Column("stock", sa.Integer(), nullable=False),
        sa.Column("locked_stock", sa.Integer(), nullable=False),
        sa.Column("main_image", sa.String(length=512), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["product_id"], ["product.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("sku_code", name="uq_product_sku_code"),
    )
    op.create_index("ix_product_sku_pk", "product_sku", ["id"], unique=False)
    op.create_index("ix_product_sku_product_fk", "product_sku", ["product_id"], unique=False)
    op.create_index("ix_product_sku_code", "product_sku", ["sku_code"], unique=False)
    op.create_index("ix_product_sku_status", "product_sku", ["status"], unique=False)

    op.create_table(
        "inventory_log",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("sku_id", sa.Integer(), nullable=False),
        sa.Column("change_type", sa.String(length=32), nullable=False),
        sa.Column("change_quantity", sa.Integer(), nullable=False),
        sa.Column("stock_before", sa.Integer(), nullable=False),
        sa.Column("stock_after", sa.Integer(), nullable=False),
        sa.Column("related_type", sa.String(length=64), nullable=True),
        sa.Column("related_id", sa.String(length=64), nullable=True),
        sa.Column("remark", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["product_id"], ["product.id"]),
        sa.ForeignKeyConstraint(["sku_id"], ["product_sku.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_inventory_log_pk", "inventory_log", ["id"], unique=False)
    op.create_index("ix_inventory_log_product_fk", "inventory_log", ["product_id"], unique=False)
    op.create_index("ix_inventory_log_sku_fk", "inventory_log", ["sku_id"], unique=False)
    op.create_index("ix_inventory_log_change_type", "inventory_log", ["change_type"], unique=False)
    op.create_index("ix_inventory_log_related_type", "inventory_log", ["related_type"], unique=False)
    op.create_index("ix_inventory_log_related_id", "inventory_log", ["related_id"], unique=False)

    categories = [
        ("cat_zone", "\u732b\u54aa\u4e13\u533a", 10),
        ("dog_zone", "\u72d7\u72d7\u4e13\u533a", 20),
        ("small_pet_zone", "\u5c0f\u5ba0\u4e13\u533a", 30),
        ("aquarium_zone", "\u6c34\u65cf\u4e13\u533a", 40),
        ("bird_zone", "\u9e1f\u7c7b\u4e13\u533a", 50),
        ("reptile_zone", "\u722c\u5ba0\u4e13\u533a", 60),
        ("pet_food", "\u5ba0\u7269\u98df\u54c1", 70),
        ("pet_snacks", "\u5ba0\u7269\u96f6\u98df", 80),
        ("pet_toys", "\u5ba0\u7269\u73a9\u5177", 90),
        ("pet_clothes", "\u5ba0\u7269\u670d\u9970", 100),
        ("travel_supplies", "\u51fa\u884c\u7528\u54c1", 110),
        ("cleaning_care", "\u6e05\u6d01\u6d17\u62a4", 120),
        ("cat_litter_toilet", "\u732b\u7802\u5395\u6240", 130),
        ("cage_bed", "\u7b3c\u820d\u7a9d\u57ab", 140),
        ("medical_health", "\u533b\u7597\u4fdd\u5065", 150),
        ("smart_device", "\u667a\u80fd\u8bbe\u5907", 160),
        ("pet_peripheral", "\u5ba0\u7269\u5468\u8fb9", 170),
        ("owner_peripheral", "\u4e3b\u4eba\u5468\u8fb9", 180),
    ]
    op.bulk_insert(
        sa.table(
            "product_category",
            sa.column("parent_id", sa.Integer),
            sa.column("name", sa.String),
            sa.column("code", sa.String),
            sa.column("sort_order", sa.Integer),
            sa.column("icon_url", sa.String),
            sa.column("status", sa.String),
            sa.column("created_at", sa.DateTime(timezone=True)),
            sa.column("updated_at", sa.DateTime(timezone=True)),
            sa.column("deleted_at", sa.DateTime(timezone=True)),
        ),
        [
            {
                "parent_id": None,
                "name": name,
                "code": code,
                "sort_order": sort_order,
                "icon_url": None,
                "status": "active",
                **_timestamps(),
            }
            for code, name, sort_order in categories
        ],
    )


def downgrade() -> None:
    op.drop_index("ix_inventory_log_related_id", table_name="inventory_log")
    op.drop_index("ix_inventory_log_related_type", table_name="inventory_log")
    op.drop_index("ix_inventory_log_change_type", table_name="inventory_log")
    op.drop_index("ix_inventory_log_sku_fk", table_name="inventory_log")
    op.drop_index("ix_inventory_log_product_fk", table_name="inventory_log")
    op.drop_index("ix_inventory_log_pk", table_name="inventory_log")
    op.drop_table("inventory_log")

    op.drop_index("ix_product_sku_status", table_name="product_sku")
    op.drop_index("ix_product_sku_code", table_name="product_sku")
    op.drop_index("ix_product_sku_product_fk", table_name="product_sku")
    op.drop_index("ix_product_sku_pk", table_name="product_sku")
    op.drop_table("product_sku")

    op.drop_index("ix_product_status", table_name="product")
    op.drop_index("ix_product_sales_count", table_name="product")
    op.drop_index("ix_product_price_cent", table_name="product")
    op.drop_index("ix_product_title", table_name="product")
    op.drop_index("ix_product_brand_fk", table_name="product")
    op.drop_index("ix_product_category_fk", table_name="product")
    op.drop_index("ix_product_merchant_id", table_name="product")
    op.drop_index("ix_product_pk", table_name="product")
    op.drop_table("product")

    op.drop_index("ix_brand_status", table_name="brand")
    op.drop_index("ix_brand_name", table_name="brand")
    op.drop_index("ix_brand_pk", table_name="brand")
    op.drop_table("brand")

    op.drop_index("ix_product_category_status", table_name="product_category")
    op.drop_index("ix_product_category_code", table_name="product_category")
    op.drop_index("ix_product_category_name", table_name="product_category")
    op.drop_index("ix_product_category_parent_id", table_name="product_category")
    op.drop_index("ix_product_category_pk", table_name="product_category")
    op.drop_table("product_category")
