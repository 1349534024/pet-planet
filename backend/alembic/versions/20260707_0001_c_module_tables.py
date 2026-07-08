"""add c module tables

Revision ID: 20260707_0001
Revises: 20260707_0005
Create Date: 2026-07-07 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260707_0001"
down_revision: str | None = "20260707_0005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def timestamps() -> list[sa.Column]:
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    ]


def audit_columns() -> list[sa.Column]:
    return [
        sa.Column("audit_status", sa.String(length=32), nullable=False),
        sa.Column("audit_reason", sa.String(length=255), nullable=True),
        sa.Column("audited_by", sa.Integer(), nullable=True),
        sa.Column("audited_at", sa.DateTime(timezone=True), nullable=True),
    ]


def create_indexed_fk(table: str, column: str, target: str) -> None:
    if op.get_bind().dialect.name != "sqlite":
        op.create_foreign_key(f"fk_{table}_{column}", table, target, [column], ["id"])
    op.create_index(f"ix_{table}_{column}", table, [column])


def upgrade() -> None:
    op.create_table(
        "merchant",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("merchant_type", sa.String(length=32), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("contact_name", sa.String(length=64), nullable=False),
        sa.Column("contact_phone", sa.String(length=32), nullable=False),
        sa.Column("city", sa.String(length=64), nullable=True),
        sa.Column("address", sa.String(length=255), nullable=True),
        sa.Column("business_scope", sa.String(length=255), nullable=True),
        sa.Column("settlement_account", sa.String(length=255), nullable=True),
        sa.Column("deposit_status", sa.String(length=32), nullable=False),
        *audit_columns(),
        sa.Column("status", sa.String(length=32), nullable=False),
        *timestamps(),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_merchant_audit_status", "merchant", ["audit_status"])
    op.create_index("ix_merchant_id", "merchant", ["id"])
    op.create_index("ix_merchant_merchant_type", "merchant", ["merchant_type"])
    op.create_index("ix_merchant_name", "merchant", ["name"])
    create_indexed_fk("merchant", "owner_id", "user")
    create_indexed_fk("merchant", "audited_by", "user")

    op.create_table(
        "merchant_qualification",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("merchant_id", sa.Integer(), nullable=False),
        sa.Column("qualification_type", sa.String(length=64), nullable=False),
        sa.Column("file_asset_id", sa.Integer(), nullable=True),
        sa.Column("certificate_no", sa.String(length=128), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        *audit_columns(),
        sa.Column("status", sa.String(length=32), nullable=False),
        *timestamps(),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_merchant_qualification_audit_status", "merchant_qualification", ["audit_status"])
    op.create_index("ix_merchant_qualification_id", "merchant_qualification", ["id"])
    op.create_index("ix_merchant_qualification_qualification_type", "merchant_qualification", ["qualification_type"])
    create_indexed_fk("merchant_qualification", "merchant_id", "merchant")
    create_indexed_fk("merchant_qualification", "file_asset_id", "file_asset")
    create_indexed_fk("merchant_qualification", "audited_by", "user")

    op.create_table(
        "merchant_store",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("merchant_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("province", sa.String(length=64), nullable=True),
        sa.Column("city", sa.String(length=64), nullable=True),
        sa.Column("district", sa.String(length=64), nullable=True),
        sa.Column("address", sa.String(length=255), nullable=False),
        sa.Column("contact_phone", sa.String(length=32), nullable=True),
        sa.Column("cover_file_asset_id", sa.Integer(), nullable=True),
        sa.Column("longitude", sa.String(length=32), nullable=True),
        sa.Column("latitude", sa.String(length=32), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        *timestamps(),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_merchant_store_id", "merchant_store", ["id"])
    create_indexed_fk("merchant_store", "merchant_id", "merchant")
    create_indexed_fk("merchant_store", "cover_file_asset_id", "file_asset")

    op.create_table(
        "adoption_pet",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("publisher_id", sa.Integer(), nullable=False),
        sa.Column("merchant_id", sa.Integer(), nullable=True),
        sa.Column("name", sa.String(length=64), nullable=False),
        sa.Column("type", sa.String(length=32), nullable=False),
        sa.Column("breed", sa.String(length=64), nullable=True),
        sa.Column("gender", sa.String(length=16), nullable=False),
        sa.Column("age_desc", sa.String(length=64), nullable=True),
        sa.Column("city", sa.String(length=64), nullable=True),
        sa.Column("health_status", sa.String(length=255), nullable=True),
        sa.Column("vaccine_status", sa.String(length=32), nullable=False),
        sa.Column("deworm_status", sa.String(length=32), nullable=False),
        sa.Column("sterilized", sa.String(length=16), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("adoption_requirements", sa.Text(), nullable=True),
        sa.Column("media_asset_ids", sa.String(length=512), nullable=True),
        *audit_columns(),
        sa.Column("status", sa.String(length=32), nullable=False),
        *timestamps(),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_adoption_pet_audit_status", "adoption_pet", ["audit_status"])
    op.create_index("ix_adoption_pet_city", "adoption_pet", ["city"])
    op.create_index("ix_adoption_pet_id", "adoption_pet", ["id"])
    op.create_index("ix_adoption_pet_type", "adoption_pet", ["type"])
    create_indexed_fk("adoption_pet", "publisher_id", "user")
    create_indexed_fk("adoption_pet", "merchant_id", "merchant")
    create_indexed_fk("adoption_pet", "audited_by", "user")

    op.create_table(
        "adoption_application",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("adoption_pet_id", sa.Integer(), nullable=False),
        sa.Column("applicant_id", sa.Integer(), nullable=False),
        sa.Column("real_name", sa.String(length=64), nullable=False),
        sa.Column("phone", sa.String(length=32), nullable=False),
        sa.Column("city", sa.String(length=64), nullable=True),
        sa.Column("housing_status", sa.String(length=64), nullable=True),
        sa.Column("pet_experience", sa.Text(), nullable=True),
        sa.Column("monthly_budget", sa.String(length=64), nullable=True),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("accept_follow_up", sa.String(length=16), nullable=False),
        sa.Column("accept_agreement", sa.String(length=16), nullable=False),
        *audit_columns(),
        sa.Column("status", sa.String(length=32), nullable=False),
        *timestamps(),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_adoption_application_audit_status", "adoption_application", ["audit_status"])
    op.create_index("ix_adoption_application_id", "adoption_application", ["id"])
    create_indexed_fk("adoption_application", "adoption_pet_id", "adoption_pet")
    create_indexed_fk("adoption_application", "applicant_id", "user")
    create_indexed_fk("adoption_application", "audited_by", "user")

    op.create_table(
        "adoption_agreement",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("application_id", sa.Integer(), nullable=False),
        sa.Column("file_asset_id", sa.Integer(), nullable=True),
        sa.Column("signed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        *timestamps(),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_adoption_agreement_id", "adoption_agreement", ["id"])
    create_indexed_fk("adoption_agreement", "application_id", "adoption_application")
    create_indexed_fk("adoption_agreement", "file_asset_id", "file_asset")

    op.create_table(
        "adoption_handover",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("application_id", sa.Integer(), nullable=False),
        sa.Column("handover_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("handover_location", sa.String(length=255), nullable=True),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("media_asset_ids", sa.String(length=512), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        *timestamps(),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_adoption_handover_id", "adoption_handover", ["id"])
    create_indexed_fk("adoption_handover", "application_id", "adoption_application")

    op.create_table(
        "adoption_follow_up",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("application_id", sa.Integer(), nullable=False),
        sa.Column("follow_up_type", sa.String(length=32), nullable=False),
        sa.Column("planned_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column("media_asset_ids", sa.String(length=512), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        *timestamps(),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_adoption_follow_up_follow_up_type", "adoption_follow_up", ["follow_up_type"])
    op.create_index("ix_adoption_follow_up_id", "adoption_follow_up", ["id"])
    create_indexed_fk("adoption_follow_up", "application_id", "adoption_application")

    op.create_table(
        "live_pet",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("merchant_id", sa.Integer(), nullable=False),
        sa.Column("publisher_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=64), nullable=False),
        sa.Column("type", sa.String(length=32), nullable=False),
        sa.Column("breed", sa.String(length=64), nullable=True),
        sa.Column("gender", sa.String(length=16), nullable=False),
        sa.Column("birthday", sa.Date(), nullable=True),
        sa.Column("color", sa.String(length=64), nullable=True),
        sa.Column("weight", sa.String(length=32), nullable=True),
        sa.Column("city", sa.String(length=64), nullable=True),
        sa.Column("price_cent", sa.Integer(), nullable=False),
        sa.Column("deposit_cent", sa.Integer(), nullable=False),
        sa.Column("vaccine_status", sa.String(length=32), nullable=False),
        sa.Column("deworm_status", sa.String(length=32), nullable=False),
        sa.Column("health_desc", sa.Text(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("support_video_view", sa.String(length=16), nullable=False),
        sa.Column("support_offline_view", sa.String(length=16), nullable=False),
        *audit_columns(),
        sa.Column("status", sa.String(length=32), nullable=False),
        *timestamps(),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_live_pet_audit_status", "live_pet", ["audit_status"])
    op.create_index("ix_live_pet_city", "live_pet", ["city"])
    op.create_index("ix_live_pet_id", "live_pet", ["id"])
    op.create_index("ix_live_pet_type", "live_pet", ["type"])
    create_indexed_fk("live_pet", "merchant_id", "merchant")
    create_indexed_fk("live_pet", "publisher_id", "user")
    create_indexed_fk("live_pet", "audited_by", "user")

    op.create_table(
        "live_pet_media",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("live_pet_id", sa.Integer(), nullable=False),
        sa.Column("file_asset_id", sa.Integer(), nullable=True),
        sa.Column("media_type", sa.String(length=32), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        *timestamps(),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_live_pet_media_id", "live_pet_media", ["id"])
    op.create_index("ix_live_pet_media_media_type", "live_pet_media", ["media_type"])
    create_indexed_fk("live_pet_media", "live_pet_id", "live_pet")
    create_indexed_fk("live_pet_media", "file_asset_id", "file_asset")

    op.create_table(
        "live_pet_certificate",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("live_pet_id", sa.Integer(), nullable=False),
        sa.Column("certificate_type", sa.String(length=64), nullable=False),
        sa.Column("file_asset_id", sa.Integer(), nullable=True),
        sa.Column("certificate_no", sa.String(length=128), nullable=True),
        sa.Column("issued_at", sa.Date(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        *timestamps(),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_live_pet_certificate_certificate_type", "live_pet_certificate", ["certificate_type"])
    op.create_index("ix_live_pet_certificate_id", "live_pet_certificate", ["id"])
    create_indexed_fk("live_pet_certificate", "live_pet_id", "live_pet")
    create_indexed_fk("live_pet_certificate", "file_asset_id", "file_asset")

    op.create_table(
        "service_item",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("merchant_id", sa.Integer(), nullable=False),
        sa.Column("store_id", sa.Integer(), nullable=True),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("service_type", sa.String(length=32), nullable=False),
        sa.Column("price_cent", sa.Integer(), nullable=False),
        sa.Column("duration_minutes", sa.Integer(), nullable=True),
        sa.Column("applicable_pet_type", sa.String(length=64), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("refund_rule", sa.Text(), nullable=True),
        *audit_columns(),
        sa.Column("status", sa.String(length=32), nullable=False),
        *timestamps(),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_service_item_audit_status", "service_item", ["audit_status"])
    op.create_index("ix_service_item_id", "service_item", ["id"])
    op.create_index("ix_service_item_name", "service_item", ["name"])
    op.create_index("ix_service_item_service_type", "service_item", ["service_type"])
    create_indexed_fk("service_item", "merchant_id", "merchant")
    create_indexed_fk("service_item", "store_id", "merchant_store")
    create_indexed_fk("service_item", "audited_by", "user")

    op.create_table(
        "service_schedule",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("service_item_id", sa.Integer(), nullable=False),
        sa.Column("start_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("capacity", sa.Integer(), nullable=False),
        sa.Column("booked_count", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        *timestamps(),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_service_schedule_end_at", "service_schedule", ["end_at"])
    op.create_index("ix_service_schedule_id", "service_schedule", ["id"])
    op.create_index("ix_service_schedule_start_at", "service_schedule", ["start_at"])
    create_indexed_fk("service_schedule", "service_item_id", "service_item")

    op.create_table(
        "service_booking",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("pet_id", sa.Integer(), nullable=True),
        sa.Column("service_item_id", sa.Integer(), nullable=False),
        sa.Column("schedule_id", sa.Integer(), nullable=True),
        sa.Column("contact_name", sa.String(length=64), nullable=False),
        sa.Column("contact_phone", sa.String(length=32), nullable=False),
        sa.Column("remark", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        *timestamps(),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_service_booking_id", "service_booking", ["id"])
    op.create_index("ix_service_booking_status", "service_booking", ["status"])
    create_indexed_fk("service_booking", "user_id", "user")
    create_indexed_fk("service_booking", "pet_id", "pet_profile")
    create_indexed_fk("service_booking", "service_item_id", "service_item")
    create_indexed_fk("service_booking", "schedule_id", "service_schedule")

    op.create_table(
        "service_report",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("booking_id", sa.Integer(), nullable=False),
        sa.Column("reporter_id", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column("before_media_asset_ids", sa.String(length=512), nullable=True),
        sa.Column("during_media_asset_ids", sa.String(length=512), nullable=True),
        sa.Column("after_media_asset_ids", sa.String(length=512), nullable=True),
        sa.Column("abnormal_note", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        *timestamps(),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_service_report_id", "service_report", ["id"])
    create_indexed_fk("service_report", "booking_id", "service_booking")
    create_indexed_fk("service_report", "reporter_id", "user")


def downgrade() -> None:
    for table in [
        "service_report",
        "service_booking",
        "service_schedule",
        "service_item",
        "live_pet_certificate",
        "live_pet_media",
        "live_pet",
        "adoption_follow_up",
        "adoption_handover",
        "adoption_agreement",
        "adoption_application",
        "adoption_pet",
        "merchant_store",
        "merchant_qualification",
        "merchant",
    ]:
        op.drop_table(table)
