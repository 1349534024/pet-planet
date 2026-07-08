"""add admin audit tables

Revision ID: 20260706_2249
Revises: 20260707_0006_report_media
Create Date: 2026-07-06 22:49:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260706_2249"
down_revision: str | None = "20260707_0006_report_media"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _timestamps() -> list[sa.Column]:
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    ]


def _create_indexes(table_name: str, columns: list[str]) -> None:
    for column in columns:
        op.create_index(op.f(f"ix_{table_name}_{column}"), table_name, [column], unique=False)


def _drop_indexes(table_name: str, columns: list[str]) -> None:
    for column in columns:
        op.drop_index(op.f(f"ix_{table_name}_{column}"), table_name=table_name)


def upgrade() -> None:
    op.create_table(
        "admin_user",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("username", sa.String(length=64), nullable=False),
        sa.Column("display_name", sa.String(length=64), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        *_timestamps(),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
        sa.UniqueConstraint("username"),
    )
    _create_indexes("admin_user", ["id", "user_id", "username", "status"])

    op.create_table(
        "admin_role",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        *_timestamps(),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )
    _create_indexes("admin_role", ["id", "code", "status"])

    op.create_table(
        "admin_permission",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=128), nullable=False),
        sa.Column("name", sa.String(length=64), nullable=False),
        sa.Column("module", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        *_timestamps(),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )
    _create_indexes("admin_permission", ["id", "code", "module", "status"])

    op.create_table(
        "admin_user_role",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("admin_user_id", sa.Integer(), nullable=False),
        sa.Column("role_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        *_timestamps(),
        sa.ForeignKeyConstraint(["admin_user_id"], ["admin_user.id"]),
        sa.ForeignKeyConstraint(["role_id"], ["admin_role.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("admin_user_id", "role_id", name="uq_admin_user_role"),
    )
    _create_indexes("admin_user_role", ["id", "admin_user_id", "role_id", "status"])

    op.create_table(
        "admin_role_permission",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("role_id", sa.Integer(), nullable=False),
        sa.Column("permission_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        *_timestamps(),
        sa.ForeignKeyConstraint(["permission_id"], ["admin_permission.id"]),
        sa.ForeignKeyConstraint(["role_id"], ["admin_role.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("role_id", "permission_id", name="uq_admin_role_permission"),
    )
    _create_indexes("admin_role_permission", ["id", "role_id", "permission_id", "status"])

    op.create_table(
        "admin_permission_dependency",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("permission_id", sa.Integer(), nullable=False),
        sa.Column("depends_on_permission_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        *_timestamps(),
        sa.ForeignKeyConstraint(["depends_on_permission_id"], ["admin_permission.id"]),
        sa.ForeignKeyConstraint(["permission_id"], ["admin_permission.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("permission_id", "depends_on_permission_id", name="uq_admin_permission_dependency"),
    )
    _create_indexes(
        "admin_permission_dependency",
        ["id", "permission_id", "depends_on_permission_id", "status"],
    )

    op.create_table(
        "audit_task",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("business_type", sa.String(length=64), nullable=False),
        sa.Column("target_type", sa.String(length=64), nullable=False),
        sa.Column("target_id", sa.String(length=64), nullable=False),
        sa.Column("submitter_id", sa.Integer(), nullable=True),
        sa.Column("reviewer_id", sa.Integer(), nullable=True),
        sa.Column("title", sa.String(length=128), nullable=False),
        sa.Column("snapshot_data", sa.Text(), nullable=True),
        sa.Column("risk_level", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("decision", sa.String(length=32), nullable=True),
        sa.Column("reason", sa.String(length=255), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        *_timestamps(),
        sa.ForeignKeyConstraint(["reviewer_id"], ["user.id"]),
        sa.ForeignKeyConstraint(["submitter_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    _create_indexes(
        "audit_task",
        [
            "id",
            "business_type",
            "target_type",
            "target_id",
            "submitter_id",
            "reviewer_id",
            "risk_level",
            "status",
            "decision",
            "reviewed_at",
        ],
    )

    op.create_table(
        "audit_record",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("audit_task_id", sa.Integer(), nullable=False),
        sa.Column("reviewer_id", sa.Integer(), nullable=True),
        sa.Column("action", sa.String(length=32), nullable=False),
        sa.Column("reason", sa.String(length=255), nullable=True),
        sa.Column("sync_status", sa.String(length=32), nullable=False),
        sa.Column("sync_message", sa.String(length=255), nullable=True),
        sa.Column("before_data", sa.Text(), nullable=True),
        sa.Column("after_data", sa.Text(), nullable=True),
        *_timestamps(),
        sa.ForeignKeyConstraint(["audit_task_id"], ["audit_task.id"]),
        sa.ForeignKeyConstraint(["reviewer_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    _create_indexes("audit_record", ["id", "audit_task_id", "reviewer_id", "action", "sync_status"])

    op.create_table(
        "risk_rule",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("rule_type", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("pattern", sa.String(length=255), nullable=False),
        sa.Column("risk_level", sa.String(length=32), nullable=False),
        sa.Column("action", sa.String(length=32), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        *_timestamps(),
        sa.PrimaryKeyConstraint("id"),
    )
    _create_indexes("risk_rule", ["id", "rule_type", "risk_level", "enabled", "status"])

    op.create_table(
        "risk_event",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("target_type", sa.String(length=64), nullable=True),
        sa.Column("target_id", sa.String(length=64), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("rule_id", sa.Integer(), nullable=True),
        sa.Column("risk_level", sa.String(length=32), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column("evidence_data", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        *_timestamps(),
        sa.ForeignKeyConstraint(["rule_id"], ["risk_rule.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    _create_indexes(
        "risk_event",
        ["id", "event_type", "target_type", "target_id", "user_id", "rule_id", "risk_level", "status"],
    )

    op.create_table(
        "report_case",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("reporter_id", sa.Integer(), nullable=True),
        sa.Column("target_type", sa.String(length=64), nullable=False),
        sa.Column("target_id", sa.String(length=64), nullable=False),
        sa.Column("reason_type", sa.String(length=64), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("resolution_action", sa.String(length=32), nullable=True),
        sa.Column("handle_reason", sa.String(length=255), nullable=True),
        sa.Column("handler_id", sa.Integer(), nullable=True),
        sa.Column("handled_at", sa.DateTime(timezone=True), nullable=True),
        *_timestamps(),
        sa.ForeignKeyConstraint(["handler_id"], ["user.id"]),
        sa.ForeignKeyConstraint(["reporter_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    _create_indexes(
        "report_case",
        [
            "id",
            "reporter_id",
            "target_type",
            "target_id",
            "reason_type",
            "status",
            "resolution_action",
            "handler_id",
            "handled_at",
        ],
    )

    op.create_table(
        "blacklist",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("target_type", sa.String(length=64), nullable=False),
        sa.Column("target_id", sa.String(length=64), nullable=False),
        sa.Column("reason", sa.String(length=255), nullable=True),
        sa.Column("operator_id", sa.Integer(), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        *_timestamps(),
        sa.ForeignKeyConstraint(["operator_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    _create_indexes("blacklist", ["id", "target_type", "target_id", "operator_id", "expires_at", "status"])

    op.create_table(
        "message_template",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("title_template", sa.String(length=128), nullable=False),
        sa.Column("content_template", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        *_timestamps(),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )
    _create_indexes("message_template", ["id", "code", "status"])

    op.create_table(
        "message",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("receiver_id", sa.Integer(), nullable=True),
        sa.Column("message_type", sa.String(length=64), nullable=False),
        sa.Column("title", sa.String(length=128), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("related_type", sa.String(length=64), nullable=True),
        sa.Column("related_id", sa.String(length=64), nullable=True),
        sa.Column("is_read", sa.Boolean(), nullable=False),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        *_timestamps(),
        sa.ForeignKeyConstraint(["receiver_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    _create_indexes("message", ["id", "receiver_id", "message_type", "related_type", "related_id", "is_read", "status"])

    op.create_table(
        "notification_task",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("template_id", sa.Integer(), nullable=True),
        sa.Column("receiver_id", sa.Integer(), nullable=True),
        sa.Column("channel", sa.String(length=32), nullable=False),
        sa.Column("payload_data", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("status_reason", sa.String(length=255), nullable=True),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        *_timestamps(),
        sa.ForeignKeyConstraint(["receiver_id"], ["user.id"]),
        sa.ForeignKeyConstraint(["template_id"], ["message_template.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    _create_indexes(
        "notification_task",
        ["id", "template_id", "receiver_id", "channel", "status", "scheduled_at", "sent_at"],
    )

    op.create_table(
        "operation_config",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("config_key", sa.String(length=128), nullable=False),
        sa.Column("config_value", sa.Text(), nullable=False),
        sa.Column("config_type", sa.String(length=64), nullable=False),
        sa.Column("config_schema", sa.Text(), nullable=True),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column("operator_id", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        *_timestamps(),
        sa.ForeignKeyConstraint(["operator_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("config_key", name="uq_operation_config_key"),
    )
    _create_indexes("operation_config", ["id", "config_key", "config_type", "operator_id", "status"])

    op.create_table(
        "statistics_snapshot",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("snapshot_type", sa.String(length=64), nullable=False),
        sa.Column("metric_date", sa.String(length=32), nullable=False),
        sa.Column("new_users", sa.Integer(), nullable=False),
        sa.Column("active_users", sa.Integer(), nullable=False),
        sa.Column("gmv_cent", sa.Integer(), nullable=False),
        sa.Column("order_count", sa.Integer(), nullable=False),
        sa.Column("repurchase_count", sa.Integer(), nullable=False),
        sa.Column("content_count", sa.Integer(), nullable=False),
        sa.Column("adoption_success_count", sa.Integer(), nullable=False),
        sa.Column("complaint_count", sa.Integer(), nullable=False),
        sa.Column("after_sale_count", sa.Integer(), nullable=False),
        sa.Column("extra_data", sa.Text(), nullable=True),
        *_timestamps(),
        sa.PrimaryKeyConstraint("id"),
    )
    _create_indexes("statistics_snapshot", ["id", "snapshot_type", "metric_date"])

    op.create_table(
        "data_event",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("source", sa.String(length=64), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("target_type", sa.String(length=64), nullable=True),
        sa.Column("target_id", sa.String(length=64), nullable=True),
        sa.Column("event_data", sa.Text(), nullable=True),
        *_timestamps(),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    _create_indexes("data_event", ["id", "event_type", "source", "user_id", "target_type", "target_id"])


def downgrade() -> None:
    drop_order = [
        ("data_event", ["id", "event_type", "source", "user_id", "target_type", "target_id"]),
        ("statistics_snapshot", ["id", "snapshot_type", "metric_date"]),
        ("operation_config", ["id", "config_key", "config_type", "operator_id", "status"]),
        ("notification_task", ["id", "template_id", "receiver_id", "channel", "status", "scheduled_at", "sent_at"]),
        ("message", ["id", "receiver_id", "message_type", "related_type", "related_id", "is_read", "status"]),
        ("message_template", ["id", "code", "status"]),
        ("blacklist", ["id", "target_type", "target_id", "operator_id", "expires_at", "status"]),
        (
            "report_case",
            [
                "id",
                "reporter_id",
                "target_type",
                "target_id",
                "reason_type",
                "status",
                "resolution_action",
                "handler_id",
                "handled_at",
            ],
        ),
        ("risk_event", ["id", "event_type", "target_type", "target_id", "user_id", "rule_id", "risk_level", "status"]),
        ("risk_rule", ["id", "rule_type", "risk_level", "enabled", "status"]),
        ("audit_record", ["id", "audit_task_id", "reviewer_id", "action", "sync_status"]),
        (
            "audit_task",
            [
                "id",
                "business_type",
                "target_type",
                "target_id",
                "submitter_id",
                "reviewer_id",
                "risk_level",
                "status",
                "decision",
                "reviewed_at",
            ],
        ),
        ("admin_permission_dependency", ["id", "permission_id", "depends_on_permission_id", "status"]),
        ("admin_role_permission", ["id", "role_id", "permission_id", "status"]),
        ("admin_user_role", ["id", "admin_user_id", "role_id", "status"]),
        ("admin_permission", ["id", "code", "module", "status"]),
        ("admin_role", ["id", "code", "status"]),
        ("admin_user", ["id", "user_id", "username", "status"]),
    ]
    for table_name, columns in drop_order:
        _drop_indexes(table_name, columns)
        op.drop_table(table_name)
