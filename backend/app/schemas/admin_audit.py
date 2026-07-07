from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field, field_validator

from app.schemas.common import ORMModel


class AuditTaskStatus(StrEnum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    canceled = "canceled"


class AuditDecision(StrEnum):
    approve = "approve"
    reject = "reject"
    takedown = "takedown"
    ban = "ban"
    request_changes = "request_changes"


class ReportResolutionAction(StrEnum):
    close = "close"
    warn = "warn"
    ban = "ban"
    blacklist = "blacklist"
    takedown = "takedown"


class NotificationTaskStatus(StrEnum):
    pending = "pending"
    sending = "sending"
    sent = "sent"
    failed = "failed"
    canceled = "canceled"


class OperationConfigType(StrEnum):
    text = "text"
    json = "json"
    number = "number"
    boolean = "boolean"
    list = "list"
    object = "object"


class AuditTaskCreateIn(BaseModel):
    business_type: str = Field(max_length=64)
    target_type: str = Field(max_length=64)
    target_id: str = Field(max_length=64)
    submitter_id: int | None = None
    title: str = Field(max_length=128)
    snapshot_data: str | None = None
    risk_level: str = Field(default="low", max_length=32)


class AuditDecisionIn(BaseModel):
    decision: AuditDecision
    reason: str | None = Field(default=None, max_length=255)


class AuditCancelIn(BaseModel):
    reason: str | None = Field(default=None, max_length=255)


class AuditTaskOut(ORMModel):
    id: int
    business_type: str
    target_type: str
    target_id: str
    submitter_id: int | None
    reviewer_id: int | None
    title: str
    snapshot_data: str | None
    risk_level: str
    status: str
    decision: str | None
    reason: str | None
    reviewed_at: datetime | None
    created_at: datetime
    updated_at: datetime


class AuditRecordOut(ORMModel):
    id: int
    audit_task_id: int
    reviewer_id: int | None
    action: str
    reason: str | None
    sync_status: str
    sync_message: str | None
    before_data: str | None
    after_data: str | None
    created_at: datetime


class AdminUserCreateIn(BaseModel):
    user_id: int | None = None
    username: str = Field(max_length=64)
    display_name: str | None = Field(default=None, max_length=64)


class AdminUserOut(ORMModel):
    id: int
    user_id: int | None
    username: str
    display_name: str | None
    status: str
    last_login_at: datetime | None
    created_at: datetime
    updated_at: datetime


class AdminRoleCreateIn(BaseModel):
    code: str = Field(max_length=64)
    name: str = Field(max_length=64)


class AdminRoleOut(ORMModel):
    id: int
    code: str
    name: str
    status: str
    created_at: datetime
    updated_at: datetime


class AdminPermissionCreateIn(BaseModel):
    code: str = Field(max_length=128)
    name: str = Field(max_length=64)
    module: str = Field(max_length=64)


class AdminPermissionOut(ORMModel):
    id: int
    code: str
    name: str
    module: str
    status: str
    created_at: datetime
    updated_at: datetime


class AdminUserRoleAssignIn(BaseModel):
    role_id: int


class AdminRolePermissionAssignIn(BaseModel):
    permission_id: int


class AdminPermissionDependencyCreateIn(BaseModel):
    permission_id: int
    depends_on_permission_id: int


class AdminUserRoleOut(ORMModel):
    id: int
    admin_user_id: int
    role_id: int
    status: str
    created_at: datetime
    updated_at: datetime


class AdminRolePermissionOut(ORMModel):
    id: int
    role_id: int
    permission_id: int
    status: str
    created_at: datetime
    updated_at: datetime


class AdminPermissionDependencyOut(ORMModel):
    id: int
    permission_id: int
    depends_on_permission_id: int
    status: str
    created_at: datetime
    updated_at: datetime


class RiskRuleCreateIn(BaseModel):
    rule_type: str = Field(max_length=64)
    name: str = Field(max_length=128)
    pattern: str = Field(max_length=255)
    risk_level: str = Field(default="medium", max_length=32)
    action: str = Field(default="review", max_length=32)
    enabled: bool = True


class RiskRuleOut(ORMModel):
    id: int
    rule_type: str
    name: str
    pattern: str
    risk_level: str
    action: str
    enabled: bool
    status: str
    created_at: datetime
    updated_at: datetime


class RiskEventCreateIn(BaseModel):
    event_type: str = Field(max_length=64)
    target_type: str | None = Field(default=None, max_length=64)
    target_id: str | None = Field(default=None, max_length=64)
    user_id: int | None = None
    rule_id: int | None = None
    risk_level: str = Field(default="medium", max_length=32)
    description: str | None = Field(default=None, max_length=255)
    evidence_data: str | None = None


class RiskEventOut(ORMModel):
    id: int
    event_type: str
    target_type: str | None
    target_id: str | None
    user_id: int | None
    rule_id: int | None
    risk_level: str
    description: str | None
    evidence_data: str | None
    status: str
    created_at: datetime
    updated_at: datetime


class ReportCaseCreateIn(BaseModel):
    reporter_id: int | None = None
    target_type: str = Field(max_length=64)
    target_id: str = Field(max_length=64)
    reason_type: str = Field(max_length=64)
    description: str | None = None


class ReportCaseHandleIn(BaseModel):
    status: str = Field(max_length=32)
    resolution_action: ReportResolutionAction = ReportResolutionAction.close
    reason: str | None = Field(default=None, max_length=255)
    notify_receiver_id: int | None = None
    blacklist_expires_at: datetime | None = None


class ReportCaseOut(ORMModel):
    id: int
    reporter_id: int | None
    target_type: str
    target_id: str
    reason_type: str
    description: str | None
    status: str
    resolution_action: str | None
    handle_reason: str | None
    handler_id: int | None
    handled_at: datetime | None
    created_at: datetime
    updated_at: datetime


class BlacklistCreateIn(BaseModel):
    target_type: str = Field(max_length=64)
    target_id: str = Field(max_length=64)
    reason: str | None = Field(default=None, max_length=255)
    expires_at: datetime | None = None


class BlacklistOut(ORMModel):
    id: int
    target_type: str
    target_id: str
    reason: str | None
    operator_id: int | None
    expires_at: datetime | None
    status: str
    created_at: datetime
    updated_at: datetime


class MessageCreateIn(BaseModel):
    receiver_id: int | None = None
    message_type: str = Field(max_length=64)
    title: str = Field(max_length=128)
    content: str
    related_type: str | None = Field(default=None, max_length=64)
    related_id: str | None = Field(default=None, max_length=64)


class MessageOut(ORMModel):
    id: int
    receiver_id: int | None
    message_type: str
    title: str
    content: str
    related_type: str | None
    related_id: str | None
    is_read: bool
    read_at: datetime | None
    status: str
    created_at: datetime


class MessageTemplateCreateIn(BaseModel):
    code: str = Field(max_length=64)
    name: str = Field(max_length=128)
    title_template: str = Field(max_length=128)
    content_template: str


class MessageTemplateOut(ORMModel):
    id: int
    code: str
    name: str
    title_template: str
    content_template: str
    status: str
    created_at: datetime
    updated_at: datetime


class NotificationTaskCreateIn(BaseModel):
    template_id: int | None = None
    receiver_id: int | None = None
    channel: str = Field(default="in_app", max_length=32)
    payload_data: str | None = None
    scheduled_at: datetime | None = None


class NotificationTaskStatusIn(BaseModel):
    status: NotificationTaskStatus
    reason: str | None = Field(default=None, max_length=255)


class NotificationTaskOut(ORMModel):
    id: int
    template_id: int | None
    receiver_id: int | None
    channel: str
    payload_data: str | None
    status: str
    status_reason: str | None
    scheduled_at: datetime | None
    sent_at: datetime | None
    created_at: datetime
    updated_at: datetime


class OperationConfigUpsertIn(BaseModel):
    config_key: str = Field(max_length=128)
    config_value: Any
    config_type: OperationConfigType = OperationConfigType.text
    config_schema: str | None = None
    description: str | None = Field(default=None, max_length=255)

    @field_validator("config_value")
    @classmethod
    def validate_config_value(cls, value: Any) -> Any:
        if value is None:
            raise ValueError("config_value cannot be null")
        return value


class OperationConfigOut(ORMModel):
    id: int
    config_key: str
    config_value: str
    config_type: str
    config_schema: str | None
    description: str | None
    operator_id: int | None
    status: str
    created_at: datetime
    updated_at: datetime


class StatisticsSnapshotCreateIn(BaseModel):
    snapshot_type: str = Field(default="daily", max_length=64)
    metric_date: str = Field(max_length=32)
    new_users: int = 0
    active_users: int = 0
    gmv_cent: int = 0
    order_count: int = 0
    repurchase_count: int = 0
    content_count: int = 0
    adoption_success_count: int = 0
    complaint_count: int = 0
    after_sale_count: int = 0
    extra_data: str | None = None


class StatisticsSnapshotOut(ORMModel):
    id: int
    snapshot_type: str
    metric_date: str
    new_users: int
    active_users: int
    gmv_cent: int
    order_count: int
    repurchase_count: int
    content_count: int
    adoption_success_count: int
    complaint_count: int
    after_sale_count: int
    extra_data: str | None
    created_at: datetime


class DataEventCreateIn(BaseModel):
    event_type: str = Field(max_length=64)
    source: str = Field(max_length=64)
    user_id: int | None = None
    target_type: str | None = Field(default=None, max_length=64)
    target_id: str | None = Field(default=None, max_length=64)
    event_data: str | None = None


class DataEventOut(ORMModel):
    id: int
    event_type: str
    source: str
    user_id: int | None
    target_type: str | None
    target_id: str | None
    event_data: str | None
    created_at: datetime


class StatisticsAggregateIn(BaseModel):
    snapshot_type: str = Field(default="daily", max_length=64)
    metric_date: str = Field(max_length=32)
