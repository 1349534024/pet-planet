"""add payment tables

Revision ID: 20260707_0004
Revises: 20260707_0003
Create Date: 2026-07-07
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260707_0004"
down_revision: str | None = "20260707_0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "payment_order",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("payment_no", sa.String(length=64), nullable=False),
        sa.Column("order_id", sa.Integer(), nullable=False),
        sa.Column("order_no", sa.String(length=64), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("pay_amount_cent", sa.Integer(), nullable=False),
        sa.Column("pay_channel", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("paid_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("third_party_trade_no", sa.String(length=128), nullable=True),
        sa.Column("idempotency_key", sa.String(length=128), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["order_id"], ["mall_order.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("payment_no", name="uq_payment_order_no"),
        sa.UniqueConstraint("user_id", "idempotency_key", name="uq_payment_order_user_idempotency"),
    )
    op.create_index("ix_payment_order_id", "payment_order", ["id"], unique=False)
    op.create_index("ix_payment_order_payment_no", "payment_order", ["payment_no"], unique=False)
    op.create_index("ix_payment_order_order_id", "payment_order", ["order_id"], unique=False)
    op.create_index("ix_payment_order_order_no", "payment_order", ["order_no"], unique=False)
    op.create_index("ix_payment_order_user_id", "payment_order", ["user_id"], unique=False)
    op.create_index("ix_payment_order_pay_channel", "payment_order", ["pay_channel"], unique=False)
    op.create_index("ix_payment_order_status", "payment_order", ["status"], unique=False)
    op.create_index("ix_payment_order_third_party_trade_no", "payment_order", ["third_party_trade_no"], unique=False)
    op.create_index("ix_payment_order_idempotency_key", "payment_order", ["idempotency_key"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_payment_order_idempotency_key", table_name="payment_order")
    op.drop_index("ix_payment_order_third_party_trade_no", table_name="payment_order")
    op.drop_index("ix_payment_order_status", table_name="payment_order")
    op.drop_index("ix_payment_order_pay_channel", table_name="payment_order")
    op.drop_index("ix_payment_order_user_id", table_name="payment_order")
    op.drop_index("ix_payment_order_order_no", table_name="payment_order")
    op.drop_index("ix_payment_order_order_id", table_name="payment_order")
    op.drop_index("ix_payment_order_payment_no", table_name="payment_order")
    op.drop_index("ix_payment_order_id", table_name="payment_order")
    op.drop_table("payment_order")
