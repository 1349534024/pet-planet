"""add service report during media

Revision ID: 20260707_0006_report_media
Revises: 20260707_0001
Create Date: 2026-07-07 00:10:00.000000
"""

from collections.abc import Sequence

revision: str = "20260707_0006_report_media"
down_revision: str | None = "20260707_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
