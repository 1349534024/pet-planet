"""add order fulfillment fields

Revision ID: 20260707_0005
Revises: 20260707_0004
Create Date: 2026-07-07
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260707_0005"
down_revision: str | None = "20260707_0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("mall_order", sa.Column("tracking_company", sa.String(length=64), nullable=True))
    op.add_column("mall_order", sa.Column("tracking_no", sa.String(length=128), nullable=True))
    op.add_column("mall_order", sa.Column("shipped_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("mall_order", sa.Column("received_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("mall_order", sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True))
    op.create_index("ix_mall_order_tracking_no", "mall_order", ["tracking_no"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_mall_order_tracking_no", table_name="mall_order")
    op.drop_column("mall_order", "completed_at")
    op.drop_column("mall_order", "received_at")
    op.drop_column("mall_order", "shipped_at")
    op.drop_column("mall_order", "tracking_no")
    op.drop_column("mall_order", "tracking_company")
