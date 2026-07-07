from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db, require_permission
from app.core.pagination import PageParams, get_page_params
from app.core.response import page_response, success
from app.models.user import User
from app.schemas.admin_audit import (
    AdminPermissionCreateIn,
    AdminPermissionDependencyCreateIn,
    AdminPermissionDependencyOut,
    AdminPermissionOut,
    AdminRoleCreateIn,
    AdminRoleOut,
    AdminRolePermissionAssignIn,
    AdminRolePermissionOut,
    AdminUserCreateIn,
    AdminUserOut,
    AdminUserRoleAssignIn,
    AdminUserRoleOut,
    AuditCancelIn,
    AuditDecisionIn,
    AuditRecordOut,
    AuditTaskCreateIn,
    AuditTaskOut,
    BlacklistCreateIn,
    BlacklistOut,
    DataEventCreateIn,
    DataEventOut,
    MessageCreateIn,
    MessageOut,
    MessageTemplateCreateIn,
    MessageTemplateOut,
    NotificationTaskCreateIn,
    NotificationTaskOut,
    NotificationTaskStatusIn,
    OperationConfigOut,
    OperationConfigUpsertIn,
    ReportCaseCreateIn,
    ReportCaseHandleIn,
    ReportCaseOut,
    RiskEventCreateIn,
    RiskEventOut,
    RiskRuleCreateIn,
    RiskRuleOut,
    StatisticsSnapshotCreateIn,
    StatisticsSnapshotOut,
    StatisticsAggregateIn,
)
from app.services.admin_audit_service import AdminAuditService

admin_user_router = APIRouter()
admin_role_router = APIRouter()
admin_permission_router = APIRouter()
router = APIRouter()
risk_event_router = APIRouter()
risk_rule_router = APIRouter()
report_router = APIRouter()
blacklist_router = APIRouter()
message_router = APIRouter()
message_template_router = APIRouter()
notification_router = APIRouter()
config_router = APIRouter()
statistics_router = APIRouter()


@admin_user_router.get("")
def list_admin_users(
    page: PageParams = Depends(get_page_params),
    status: str | None = Query(default=None, max_length=32),
    current_user: User = Depends(require_permission("rbac:read")),
    db: Session = Depends(get_db),
):
    items, total = AdminAuditService(db).list_admin_users(page, status)
    return page_response(
        [AdminUserOut.model_validate(item).model_dump() for item in items],
        page.page,
        page.page_size,
        total,
    )


@admin_user_router.post("")
def create_admin_user(
    payload: AdminUserCreateIn,
    current_user: User = Depends(require_permission("rbac:write")),
    db: Session = Depends(get_db),
):
    admin_user = AdminAuditService(db).create_admin_user(payload)
    return success(AdminUserOut.model_validate(admin_user).model_dump())


@admin_role_router.get("")
def list_admin_roles(
    page: PageParams = Depends(get_page_params),
    status: str | None = Query(default=None, max_length=32),
    current_user: User = Depends(require_permission("rbac:read")),
    db: Session = Depends(get_db),
):
    items, total = AdminAuditService(db).list_admin_roles(page, status)
    return page_response(
        [AdminRoleOut.model_validate(item).model_dump() for item in items],
        page.page,
        page.page_size,
        total,
    )


@admin_role_router.post("")
def create_admin_role(
    payload: AdminRoleCreateIn,
    current_user: User = Depends(require_permission("rbac:write")),
    db: Session = Depends(get_db),
):
    role = AdminAuditService(db).create_admin_role(payload)
    return success(AdminRoleOut.model_validate(role).model_dump())


@admin_permission_router.get("")
def list_admin_permissions(
    page: PageParams = Depends(get_page_params),
    module: str | None = Query(default=None, max_length=64),
    status: str | None = Query(default=None, max_length=32),
    current_user: User = Depends(require_permission("rbac:read")),
    db: Session = Depends(get_db),
):
    items, total = AdminAuditService(db).list_admin_permissions(page, module, status)
    return page_response(
        [AdminPermissionOut.model_validate(item).model_dump() for item in items],
        page.page,
        page.page_size,
        total,
    )


@admin_permission_router.post("")
def create_admin_permission(
    payload: AdminPermissionCreateIn,
    current_user: User = Depends(require_permission("rbac:write")),
    db: Session = Depends(get_db),
):
    permission = AdminAuditService(db).create_admin_permission(payload)
    return success(AdminPermissionOut.model_validate(permission).model_dump())


@admin_user_router.get("/{admin_user_id}/roles")
def list_admin_user_roles(
    admin_user_id: int,
    current_user: User = Depends(require_permission("rbac:read")),
    db: Session = Depends(get_db),
):
    items = AdminAuditService(db).list_admin_user_roles(admin_user_id)
    return success([AdminUserRoleOut.model_validate(item).model_dump() for item in items])


@admin_user_router.post("/{admin_user_id}/roles")
def assign_admin_user_role(
    admin_user_id: int,
    payload: AdminUserRoleAssignIn,
    current_user: User = Depends(require_permission("rbac:write")),
    db: Session = Depends(get_db),
):
    item = AdminAuditService(db).assign_admin_user_role(admin_user_id, payload)
    return success(AdminUserRoleOut.model_validate(item).model_dump())


@admin_role_router.get("/{role_id}/permissions")
def list_admin_role_permissions(
    role_id: int,
    current_user: User = Depends(require_permission("rbac:read")),
    db: Session = Depends(get_db),
):
    items = AdminAuditService(db).list_admin_role_permissions(role_id)
    return success([AdminRolePermissionOut.model_validate(item).model_dump() for item in items])


@admin_role_router.post("/{role_id}/permissions")
def assign_admin_role_permission(
    role_id: int,
    payload: AdminRolePermissionAssignIn,
    current_user: User = Depends(require_permission("rbac:write")),
    db: Session = Depends(get_db),
):
    items = AdminAuditService(db).assign_admin_role_permission(role_id, payload)
    return success([AdminRolePermissionOut.model_validate(item).model_dump() for item in items])


@admin_permission_router.post("/dependencies")
def create_admin_permission_dependency(
    payload: AdminPermissionDependencyCreateIn,
    current_user: User = Depends(require_permission("rbac:write")),
    db: Session = Depends(get_db),
):
    item = AdminAuditService(db).create_permission_dependency(payload)
    return success(AdminPermissionDependencyOut.model_validate(item).model_dump())


@router.get("/tasks")
def list_audit_tasks(
    page: PageParams = Depends(get_page_params),
    status: str | None = Query(default=None, max_length=32),
    business_type: str | None = Query(default=None, max_length=64),
    target_type: str | None = Query(default=None, max_length=64),
    risk_level: str | None = Query(default=None, max_length=32),
    current_user: User = Depends(require_permission("audit:read")),
    db: Session = Depends(get_db),
):
    items, total = AdminAuditService(db).list_audit_tasks(page, status, business_type, target_type, risk_level)
    return page_response(
        [AuditTaskOut.model_validate(item).model_dump() for item in items],
        page.page,
        page.page_size,
        total,
    )


@router.post("/tasks")
def create_audit_task(
    payload: AuditTaskCreateIn,
    current_user: User = Depends(require_permission("audit:claim")),
    db: Session = Depends(get_db),
):
    task = AdminAuditService(db).create_audit_task(payload)
    return success(AuditTaskOut.model_validate(task).model_dump())


@router.post("/{task_id}/decision")
def decide_audit_task(
    task_id: int,
    payload: AuditDecisionIn,
    current_user: User = Depends(require_permission("audit:decision")),
    db: Session = Depends(get_db),
):
    task = AdminAuditService(db).decide_audit_task(task_id, current_user.id, payload)
    return success(AuditTaskOut.model_validate(task).model_dump())


@router.post("/{task_id}/claim")
def claim_audit_task(
    task_id: int,
    current_user: User = Depends(require_permission("audit:claim")),
    db: Session = Depends(get_db),
):
    task = AdminAuditService(db).claim_audit_task(task_id, current_user.id)
    return success(AuditTaskOut.model_validate(task).model_dump())


@router.post("/{task_id}/cancel")
def cancel_audit_task(
    task_id: int,
    payload: AuditCancelIn,
    current_user: User = Depends(require_permission("audit:cancel")),
    db: Session = Depends(get_db),
):
    task = AdminAuditService(db).cancel_audit_task(task_id, current_user.id, payload)
    return success(AuditTaskOut.model_validate(task).model_dump())


@router.get("/records")
def list_audit_records(
    page: PageParams = Depends(get_page_params),
    audit_task_id: int | None = None,
    reviewer_id: int | None = None,
    action: str | None = Query(default=None, max_length=32),
    sync_status: str | None = Query(default=None, max_length=32),
    current_user: User = Depends(require_permission("audit:read")),
    db: Session = Depends(get_db),
):
    items, total = AdminAuditService(db).list_audit_records(page, audit_task_id, reviewer_id, action, sync_status)
    return page_response(
        [AuditRecordOut.model_validate(item).model_dump() for item in items],
        page.page,
        page.page_size,
        total,
    )


@risk_event_router.get("")
def list_risk_events(
    page: PageParams = Depends(get_page_params),
    status: str | None = Query(default=None, max_length=32),
    event_type: str | None = Query(default=None, max_length=64),
    risk_level: str | None = Query(default=None, max_length=32),
    current_user: User = Depends(require_permission("risk:read")),
    db: Session = Depends(get_db),
):
    items, total = AdminAuditService(db).list_risk_events(page, status, event_type, risk_level)
    return page_response(
        [RiskEventOut.model_validate(item).model_dump() for item in items],
        page.page,
        page.page_size,
        total,
    )


@risk_event_router.post("")
def create_risk_event(
    payload: RiskEventCreateIn,
    current_user: User = Depends(require_permission("risk:write")),
    db: Session = Depends(get_db),
):
    event = AdminAuditService(db).create_risk_event(payload)
    return success(RiskEventOut.model_validate(event).model_dump())


@risk_rule_router.get("")
def list_risk_rules(
    page: PageParams = Depends(get_page_params),
    rule_type: str | None = Query(default=None, max_length=64),
    enabled: bool | None = None,
    current_user: User = Depends(require_permission("risk:read")),
    db: Session = Depends(get_db),
):
    items, total = AdminAuditService(db).list_risk_rules(page, rule_type, enabled)
    return page_response(
        [RiskRuleOut.model_validate(item).model_dump() for item in items],
        page.page,
        page.page_size,
        total,
    )


@risk_rule_router.post("")
def create_risk_rule(
    payload: RiskRuleCreateIn,
    current_user: User = Depends(require_permission("risk:write")),
    db: Session = Depends(get_db),
):
    rule = AdminAuditService(db).create_risk_rule(payload)
    return success(RiskRuleOut.model_validate(rule).model_dump())


@report_router.get("")
def list_report_cases(
    page: PageParams = Depends(get_page_params),
    status: str | None = Query(default=None, max_length=32),
    target_type: str | None = Query(default=None, max_length=64),
    reason_type: str | None = Query(default=None, max_length=64),
    current_user: User = Depends(require_permission("risk:read")),
    db: Session = Depends(get_db),
):
    items, total = AdminAuditService(db).list_report_cases(page, status, target_type, reason_type)
    return page_response(
        [ReportCaseOut.model_validate(item).model_dump() for item in items],
        page.page,
        page.page_size,
        total,
    )


@report_router.post("")
def create_report_case(
    payload: ReportCaseCreateIn,
    current_user: User = Depends(require_permission("risk:write")),
    db: Session = Depends(get_db),
):
    data = payload.model_copy(update={"reporter_id": payload.reporter_id or current_user.id})
    report = AdminAuditService(db).create_report_case(data)
    return success(ReportCaseOut.model_validate(report).model_dump())


@report_router.post("/{report_id}/handle")
def handle_report_case(
    report_id: int,
    payload: ReportCaseHandleIn,
    current_user: User = Depends(require_permission("risk:write")),
    db: Session = Depends(get_db),
):
    report = AdminAuditService(db).handle_report_case(report_id, current_user.id, payload)
    return success(ReportCaseOut.model_validate(report).model_dump())


@blacklist_router.get("")
def list_blacklist(
    page: PageParams = Depends(get_page_params),
    target_type: str | None = Query(default=None, max_length=64),
    status: str | None = Query(default=None, max_length=32),
    current_user: User = Depends(require_permission("risk:read")),
    db: Session = Depends(get_db),
):
    items, total = AdminAuditService(db).list_blacklist(page, target_type, status)
    return page_response(
        [BlacklistOut.model_validate(item).model_dump() for item in items],
        page.page,
        page.page_size,
        total,
    )


@blacklist_router.post("")
def create_blacklist(
    payload: BlacklistCreateIn,
    current_user: User = Depends(require_permission("risk:write")),
    db: Session = Depends(get_db),
):
    item = AdminAuditService(db).create_blacklist(payload, current_user.id)
    return success(BlacklistOut.model_validate(item).model_dump())


@message_router.get("")
def list_messages(
    page: PageParams = Depends(get_page_params),
    receiver_id: int | None = None,
    is_read: bool | None = None,
    message_type: str | None = Query(default=None, max_length=64),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    role_codes = {role.code for role in current_user.roles}
    target_receiver_id = receiver_id if "admin" in role_codes else current_user.id
    items, total = AdminAuditService(db).list_messages(page, target_receiver_id, is_read, message_type)
    return page_response(
        [MessageOut.model_validate(item).model_dump() for item in items],
        page.page,
        page.page_size,
        total,
    )


@message_router.post("")
def create_message(
    payload: MessageCreateIn,
    current_user: User = Depends(require_permission("message:write")),
    db: Session = Depends(get_db),
):
    message = AdminAuditService(db).create_message(payload)
    return success(MessageOut.model_validate(message).model_dump())


@message_router.get("/unread-count")
def get_unread_message_count(
    receiver_id: int | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    role_codes = {role.code for role in current_user.roles}
    target_receiver_id = receiver_id if "admin" in role_codes else current_user.id
    return success({"unread_count": AdminAuditService(db).count_unread_messages(target_receiver_id)})


@message_router.post("/{message_id}/read")
def mark_message_read(
    message_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    message = AdminAuditService(db).mark_message_read(message_id, current_user.id)
    return success(MessageOut.model_validate(message).model_dump())


@message_template_router.get("")
def list_message_templates(
    page: PageParams = Depends(get_page_params),
    status: str | None = Query(default=None, max_length=32),
    current_user: User = Depends(require_permission("message:read")),
    db: Session = Depends(get_db),
):
    items, total = AdminAuditService(db).list_message_templates(page, status)
    return page_response(
        [MessageTemplateOut.model_validate(item).model_dump() for item in items],
        page.page,
        page.page_size,
        total,
    )


@message_template_router.post("")
def create_message_template(
    payload: MessageTemplateCreateIn,
    current_user: User = Depends(require_permission("message:write")),
    db: Session = Depends(get_db),
):
    template = AdminAuditService(db).create_message_template(payload)
    return success(MessageTemplateOut.model_validate(template).model_dump())


@message_template_router.post("/{template_id}/render")
def render_message_template(
    template_id: int,
    payload_data: str | None = None,
    current_user: User = Depends(require_permission("message:write")),
    db: Session = Depends(get_db),
):
    return success(AdminAuditService(db).render_message_template(template_id, payload_data))


@notification_router.get("")
def list_notification_tasks(
    page: PageParams = Depends(get_page_params),
    status: str | None = Query(default=None, max_length=32),
    receiver_id: int | None = None,
    current_user: User = Depends(require_permission("message:read")),
    db: Session = Depends(get_db),
):
    items, total = AdminAuditService(db).list_notification_tasks(page, status, receiver_id)
    return page_response(
        [NotificationTaskOut.model_validate(item).model_dump() for item in items],
        page.page,
        page.page_size,
        total,
    )


@notification_router.post("")
def create_notification_task(
    payload: NotificationTaskCreateIn,
    current_user: User = Depends(require_permission("message:write")),
    db: Session = Depends(get_db),
):
    task = AdminAuditService(db).create_notification_task(payload)
    return success(NotificationTaskOut.model_validate(task).model_dump())


@notification_router.post("/{task_id}/status")
def update_notification_task_status(
    task_id: int,
    payload: NotificationTaskStatusIn,
    current_user: User = Depends(require_permission("message:write")),
    db: Session = Depends(get_db),
):
    task = AdminAuditService(db).update_notification_task_status(task_id, payload)
    return success(NotificationTaskOut.model_validate(task).model_dump())


@notification_router.post("/{task_id}/send")
def send_notification_task(
    task_id: int,
    current_user: User = Depends(require_permission("message:write")),
    db: Session = Depends(get_db),
):
    task = AdminAuditService(db).send_notification_task(task_id)
    return success(NotificationTaskOut.model_validate(task).model_dump())


@config_router.get("")
def list_configs(
    page: PageParams = Depends(get_page_params),
    config_type: str | None = Query(default=None, max_length=64),
    current_user: User = Depends(require_permission("config:read")),
    db: Session = Depends(get_db),
):
    items, total = AdminAuditService(db).list_configs(page, config_type)
    return page_response(
        [OperationConfigOut.model_validate(item).model_dump() for item in items],
        page.page,
        page.page_size,
        total,
    )


@config_router.post("")
def upsert_config(
    payload: OperationConfigUpsertIn,
    current_user: User = Depends(require_permission("config:write")),
    db: Session = Depends(get_db),
):
    config = AdminAuditService(db).upsert_config(payload, current_user.id)
    return success(OperationConfigOut.model_validate(config).model_dump())


@statistics_router.get("/overview")
def get_statistics_overview(
    snapshot_type: str = Query(default="daily", max_length=64),
    current_user: User = Depends(require_permission("statistics:read")),
    db: Session = Depends(get_db),
):
    snapshot = AdminAuditService(db).get_statistics_overview(snapshot_type)
    return success(StatisticsSnapshotOut.model_validate(snapshot).model_dump() if snapshot else None)


@statistics_router.get("/events")
def list_data_events(
    page: PageParams = Depends(get_page_params),
    event_type: str | None = Query(default=None, max_length=64),
    source: str | None = Query(default=None, max_length=64),
    current_user: User = Depends(require_permission("statistics:read")),
    db: Session = Depends(get_db),
):
    items, total = AdminAuditService(db).list_data_events(page, event_type, source)
    return page_response(
        [DataEventOut.model_validate(item).model_dump() for item in items],
        page.page,
        page.page_size,
        total,
    )


@statistics_router.post("/events")
def create_data_event(
    payload: DataEventCreateIn,
    current_user: User = Depends(require_permission("statistics:read")),
    db: Session = Depends(get_db),
):
    event = AdminAuditService(db).create_data_event(payload)
    return success(DataEventOut.model_validate(event).model_dump())


@statistics_router.post("/snapshots")
def create_statistics_snapshot(
    payload: StatisticsSnapshotCreateIn,
    current_user: User = Depends(require_permission("statistics:read")),
    db: Session = Depends(get_db),
):
    snapshot = AdminAuditService(db).create_statistics_snapshot(payload)
    return success(StatisticsSnapshotOut.model_validate(snapshot).model_dump())


@statistics_router.post("/aggregate")
def aggregate_statistics_snapshot(
    payload: StatisticsAggregateIn,
    current_user: User = Depends(require_permission("statistics:read")),
    db: Session = Depends(get_db),
):
    snapshot = AdminAuditService(db).aggregate_statistics_snapshot(payload)
    return success(StatisticsSnapshotOut.model_validate(snapshot).model_dump())


@statistics_router.get("/release-checklist")
def get_release_checklist(
    current_user: User = Depends(require_permission("statistics:read")),
    db: Session = Depends(get_db),
):
    return success(AdminAuditService(db).get_release_checklist())
