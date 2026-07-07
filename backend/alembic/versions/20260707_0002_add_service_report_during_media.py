"""add service report during media

Revision ID: 20260707_0002
Revises: 20260707_0001
Create Date: 2026-07-07 00:10:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260707_0002"
down_revision: str | None = "20260707_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("service_report", sa.Column("during_media_asset_ids", sa.String(length=512), nullable=True))


def downgrade() -> None:
    op.drop_column("service_report", "during_media_asset_ids")
