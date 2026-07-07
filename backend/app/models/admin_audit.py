from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class AdminUser(Base, TimestampMixin):
    __tablename__ = "admin_user"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("user.id"), unique=True, index=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    display_name: Mapped[str | None] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(32), default="active", index=True)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class AdminRole(Base, TimestampMixin):
    __tablename__ = "admin_role"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    code: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(32), default="active", index=True)


class AdminPermission(Base, TimestampMixin):
    __tablename__ = "admin_permission"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    code: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(64))
    module: Mapped[str] = mapped_column(String(64), index=True)
    status: Mapped[str] = mapped_column(String(32), default="active", index=True)


class AdminUserRole(Base, TimestampMixin):
    __tablename__ = "admin_user_role"
    __table_args__ = (UniqueConstraint("admin_user_id", "role_id", name="uq_admin_user_role"),)

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    admin_user_id: Mapped[int] = mapped_column(ForeignKey("admin_user.id"), index=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("admin_role.id"), index=True)
    status: Mapped[str] = mapped_column(String(32), default="active", index=True)


class AdminRolePermission(Base, TimestampMixin):
    __tablename__ = "admin_role_permission"
    __table_args__ = (UniqueConstraint("role_id", "permission_id", name="uq_admin_role_permission"),)

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("admin_role.id"), index=True)
    permission_id: Mapped[int] = mapped_column(ForeignKey("admin_permission.id"), index=True)
    status: Mapped[str] = mapped_column(String(32), default="active", index=True)


class AdminPermissionDependency(Base, TimestampMixin):
    __tablename__ = "admin_permission_dependency"
    __table_args__ = (
        UniqueConstraint("permission_id", "depends_on_permission_id", name="uq_admin_permission_dependency"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    permission_id: Mapped[int] = mapped_column(ForeignKey("admin_permission.id"), index=True)
    depends_on_permission_id: Mapped[int] = mapped_column(ForeignKey("admin_permission.id"), index=True)
    status: Mapped[str] = mapped_column(String(32), default="active", index=True)


class AuditTask(Base, TimestampMixin):
    __tablename__ = "audit_task"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    business_type: Mapped[str] = mapped_column(String(64), index=True)
    target_type: Mapped[str] = mapped_column(String(64), index=True)
    target_id: Mapped[str] = mapped_column(String(64), index=True)
    submitter_id: Mapped[int | None] = mapped_column(ForeignKey("user.id"), index=True)
    reviewer_id: Mapped[int | None] = mapped_column(ForeignKey("user.id"), index=True)
    title: Mapped[str] = mapped_column(String(128))
    snapshot_data: Mapped[str | None] = mapped_column(Text)
    risk_level: Mapped[str] = mapped_column(String(32), default="low", index=True)
    status: Mapped[str] = mapped_column(String(32), default="pending", index=True)
    decision: Mapped[str | None] = mapped_column(String(32), index=True)
    reason: Mapped[str | None] = mapped_column(String(255))
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)


class AuditRecord(Base, TimestampMixin):
    __tablename__ = "audit_record"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    audit_task_id: Mapped[int] = mapped_column(ForeignKey("audit_task.id"), index=True)
    reviewer_id: Mapped[int | None] = mapped_column(ForeignKey("user.id"), index=True)
    action: Mapped[str] = mapped_column(String(32), index=True)
    reason: Mapped[str | None] = mapped_column(String(255))
    sync_status: Mapped[str] = mapped_column(String(32), default="skipped", index=True)
    sync_message: Mapped[str | None] = mapped_column(String(255))
    before_data: Mapped[str | None] = mapped_column(Text)
    after_data: Mapped[str | None] = mapped_column(Text)


class RiskRule(Base, TimestampMixin):
    __tablename__ = "risk_rule"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    rule_type: Mapped[str] = mapped_column(String(64), index=True)
    name: Mapped[str] = mapped_column(String(128))
    pattern: Mapped[str] = mapped_column(String(255))
    risk_level: Mapped[str] = mapped_column(String(32), default="medium", index=True)
    action: Mapped[str] = mapped_column(String(32), default="review")
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    status: Mapped[str] = mapped_column(String(32), default="active", index=True)


class RiskEvent(Base, TimestampMixin):
    __tablename__ = "risk_event"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    event_type: Mapped[str] = mapped_column(String(64), index=True)
    target_type: Mapped[str | None] = mapped_column(String(64), index=True)
    target_id: Mapped[str | None] = mapped_column(String(64), index=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("user.id"), index=True)
    rule_id: Mapped[int | None] = mapped_column(ForeignKey("risk_rule.id"), index=True)
    risk_level: Mapped[str] = mapped_column(String(32), default="medium", index=True)
    description: Mapped[str | None] = mapped_column(String(255))
    evidence_data: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(32), default="open", index=True)


class ReportCase(Base, TimestampMixin):
    __tablename__ = "report_case"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    reporter_id: Mapped[int | None] = mapped_column(ForeignKey("user.id"), index=True)
    target_type: Mapped[str] = mapped_column(String(64), index=True)
    target_id: Mapped[str] = mapped_column(String(64), index=True)
    reason_type: Mapped[str] = mapped_column(String(64), index=True)
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(32), default="pending", index=True)
    resolution_action: Mapped[str | None] = mapped_column(String(32), index=True)
    handle_reason: Mapped[str | None] = mapped_column(String(255))
    handler_id: Mapped[int | None] = mapped_column(ForeignKey("user.id"), index=True)
    handled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)


class Blacklist(Base, TimestampMixin):
    __tablename__ = "blacklist"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    target_type: Mapped[str] = mapped_column(String(64), index=True)
    target_id: Mapped[str] = mapped_column(String(64), index=True)
    reason: Mapped[str | None] = mapped_column(String(255))
    operator_id: Mapped[int | None] = mapped_column(ForeignKey("user.id"), index=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    status: Mapped[str] = mapped_column(String(32), default="active", index=True)


class Message(Base, TimestampMixin):
    __tablename__ = "message"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    receiver_id: Mapped[int | None] = mapped_column(ForeignKey("user.id"), index=True)
    message_type: Mapped[str] = mapped_column(String(64), index=True)
    title: Mapped[str] = mapped_column(String(128))
    content: Mapped[str] = mapped_column(Text)
    related_type: Mapped[str | None] = mapped_column(String(64), index=True)
    related_id: Mapped[str | None] = mapped_column(String(64), index=True)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(32), default="sent", index=True)


class MessageTemplate(Base, TimestampMixin):
    __tablename__ = "message_template"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    code: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(128))
    title_template: Mapped[str] = mapped_column(String(128))
    content_template: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(32), default="active", index=True)


class NotificationTask(Base, TimestampMixin):
    __tablename__ = "notification_task"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    template_id: Mapped[int | None] = mapped_column(ForeignKey("message_template.id"), index=True)
    receiver_id: Mapped[int | None] = mapped_column(ForeignKey("user.id"), index=True)
    channel: Mapped[str] = mapped_column(String(32), default="in_app", index=True)
    payload_data: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(32), default="pending", index=True)
    status_reason: Mapped[str | None] = mapped_column(String(255))
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)


class OperationConfig(Base, TimestampMixin):
    __tablename__ = "operation_config"
    __table_args__ = (UniqueConstraint("config_key", name="uq_operation_config_key"),)

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    config_key: Mapped[str] = mapped_column(String(128), index=True)
    config_value: Mapped[str] = mapped_column(Text)
    config_type: Mapped[str] = mapped_column(String(64), default="text", index=True)
    config_schema: Mapped[str | None] = mapped_column(Text)
    description: Mapped[str | None] = mapped_column(String(255))
    operator_id: Mapped[int | None] = mapped_column(ForeignKey("user.id"), index=True)
    status: Mapped[str] = mapped_column(String(32), default="active", index=True)


class StatisticsSnapshot(Base, TimestampMixin):
    __tablename__ = "statistics_snapshot"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    snapshot_type: Mapped[str] = mapped_column(String(64), index=True)
    metric_date: Mapped[str] = mapped_column(String(32), index=True)
    new_users: Mapped[int] = mapped_column(Integer, default=0)
    active_users: Mapped[int] = mapped_column(Integer, default=0)
    gmv_cent: Mapped[int] = mapped_column(Integer, default=0)
    order_count: Mapped[int] = mapped_column(Integer, default=0)
    repurchase_count: Mapped[int] = mapped_column(Integer, default=0)
    content_count: Mapped[int] = mapped_column(Integer, default=0)
    adoption_success_count: Mapped[int] = mapped_column(Integer, default=0)
    complaint_count: Mapped[int] = mapped_column(Integer, default=0)
    after_sale_count: Mapped[int] = mapped_column(Integer, default=0)
    extra_data: Mapped[str | None] = mapped_column(Text)


class DataEvent(Base, TimestampMixin):
    __tablename__ = "data_event"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    event_type: Mapped[str] = mapped_column(String(64), index=True)
    source: Mapped[str] = mapped_column(String(64), index=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("user.id"), index=True)
    target_type: Mapped[str | None] = mapped_column(String(64), index=True)
    target_id: Mapped[str | None] = mapped_column(String(64), index=True)
    event_data: Mapped[str | None] = mapped_column(Text)
