import json
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.errors import AppException, ErrorCode
from app.core.pagination import PageParams
from app.models.admin_audit import (
    AdminPermission,
    AdminPermissionDependency,
    AdminRole,
    AdminRolePermission,
    AdminUser,
    AdminUserRole,
    AuditRecord,
    AuditTask,
    Blacklist,
    Message,
    MessageTemplate,
    NotificationTask,
    OperationConfig,
    ReportCase,
    RiskEvent,
    RiskRule,
    StatisticsSnapshot,
    DataEvent,
)
from app.models.operation_log import OperationLog
from app.models.user import RealNameAuth, User
from app.repositories.admin_audit_repo import AdminAuditRepository
from app.schemas.admin_audit import (
    AdminPermissionCreateIn,
    AdminPermissionDependencyCreateIn,
    AdminRoleCreateIn,
    AdminRolePermissionAssignIn,
    AdminUserCreateIn,
    AdminUserRoleAssignIn,
    AuditCancelIn,
    AuditDecisionIn,
    AuditTaskStatus,
    AuditTaskCreateIn,
    BlacklistCreateIn,
    DataEventCreateIn,
    MessageCreateIn,
    MessageTemplateCreateIn,
    NotificationTaskCreateIn,
    NotificationTaskStatusIn,
    OperationConfigType,
    OperationConfigUpsertIn,
    ReportCaseCreateIn,
    ReportCaseHandleIn,
    RiskEventCreateIn,
    RiskRuleCreateIn,
    StatisticsAggregateIn,
    StatisticsSnapshotCreateIn,
)


class AdminAuditService:
    audit_status_flow = {
        "pending": {"processing", "completed", "canceled"},
        "processing": {"completed", "canceled"},
        "completed": set(),
        "canceled": set(),
    }
    terminal_audit_statuses = {"completed", "canceled"}
    allowed_decisions = {"approve", "reject", "takedown", "ban", "request_changes"}
    sync_status_map = {
        "real_name_auth": {
            "approve": "approved",
            "reject": "rejected",
            "request_changes": "pending",
        }
    }
    notification_status_flow = {
        "pending": {"sending", "canceled"},
        "sending": {"sent", "failed"},
        "sent": set(),
        "failed": set(),
        "canceled": set(),
    }
    statistic_event_map = {
        "new_users": "user_created",
        "active_users": "user_active",
        "order_count": "order_paid",
        "repurchase_count": "order_repurchase",
        "content_count": "content_created",
        "adoption_success_count": "adoption_success",
        "complaint_count": "report_created",
        "after_sale_count": "after_sale_created",
    }

    def __init__(self, db: Session):
        self.db = db
        self.repo = AdminAuditRepository(db)

    def _commit_and_refresh(self, *items):
        try:
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
        for item in items:
            self.db.refresh(item)

    def list_admin_users(self, page: PageParams, status: str | None = None) -> tuple[list[AdminUser], int]:
        return self.repo.list_admin_users(page, status)

    def create_admin_user(self, payload: AdminUserCreateIn) -> AdminUser:
        admin_user = self.repo.create_admin_user(AdminUser(**payload.model_dump(), status="active"))
        self._commit_and_refresh(admin_user)
        return admin_user

    def list_admin_roles(self, page: PageParams, status: str | None = None) -> tuple[list[AdminRole], int]:
        return self.repo.list_admin_roles(page, status)

    def create_admin_role(self, payload: AdminRoleCreateIn) -> AdminRole:
        role = self.repo.create_admin_role(AdminRole(**payload.model_dump(), status="active"))
        self._commit_and_refresh(role)
        return role

    def list_admin_permissions(
        self,
        page: PageParams,
        module: str | None = None,
        status: str | None = None,
    ) -> tuple[list[AdminPermission], int]:
        return self.repo.list_admin_permissions(page, module, status)

    def create_admin_permission(self, payload: AdminPermissionCreateIn) -> AdminPermission:
        permission = self.repo.create_admin_permission(AdminPermission(**payload.model_dump(), status="active"))
        self._commit_and_refresh(permission)
        return permission

    def assign_admin_user_role(self, admin_user_id: int, payload: AdminUserRoleAssignIn) -> AdminUserRole:
        admin_user = self.repo.get_admin_user(admin_user_id)
        role = self.repo.get_admin_role(payload.role_id)
        if admin_user is None or admin_user.deleted_at is not None:
            raise AppException(ErrorCode.not_found, "Admin user not found", 404)
        if role is None or role.deleted_at is not None:
            raise AppException(ErrorCode.not_found, "Admin role not found", 404)
        item = self.repo.get_admin_user_role(admin_user_id, payload.role_id)
        if item is None:
            item = AdminUserRole(admin_user_id=admin_user_id, role_id=payload.role_id, status="active")
        else:
            item.status = "active"
        saved = self.repo.save_admin_user_role(item)
        self._commit_and_refresh(saved)
        return saved

    def list_admin_user_roles(self, admin_user_id: int) -> list[AdminUserRole]:
        return self.repo.list_admin_user_roles(admin_user_id)

    def assign_admin_role_permission(
        self,
        role_id: int,
        payload: AdminRolePermissionAssignIn,
    ) -> list[AdminRolePermission]:
        role = self.repo.get_admin_role(role_id)
        permission = self.repo.get_admin_permission(payload.permission_id)
        if role is None or role.deleted_at is not None:
            raise AppException(ErrorCode.not_found, "Admin role not found", 404)
        if permission is None or permission.deleted_at is not None:
            raise AppException(ErrorCode.not_found, "Admin permission not found", 404)

        permission_ids = [payload.permission_id]
        permission_ids.extend(dep.depends_on_permission_id for dep in self.repo.list_permission_dependencies(payload.permission_id))
        saved_items: list[AdminRolePermission] = []
        for permission_id in dict.fromkeys(permission_ids):
            item = self.repo.get_admin_role_permission(role_id, permission_id)
            if item is None:
                item = AdminRolePermission(role_id=role_id, permission_id=permission_id, status="active")
            else:
                item.status = "active"
            saved_items.append(self.repo.save_admin_role_permission(item))
        self._commit_and_refresh(*saved_items)
        return saved_items

    def list_admin_role_permissions(self, role_id: int) -> list[AdminRolePermission]:
        return self.repo.list_admin_role_permissions(role_id)

    def create_permission_dependency(
        self,
        payload: AdminPermissionDependencyCreateIn,
    ) -> AdminPermissionDependency:
        if payload.permission_id == payload.depends_on_permission_id:
            raise AppException(ErrorCode.audit_invalid_status, "Permission cannot depend on itself", 400)
        permission = self.repo.get_admin_permission(payload.permission_id)
        dependency = self.repo.get_admin_permission(payload.depends_on_permission_id)
        if permission is None or permission.deleted_at is not None:
            raise AppException(ErrorCode.not_found, "Admin permission not found", 404)
        if dependency is None or dependency.deleted_at is not None:
            raise AppException(ErrorCode.not_found, "Dependent permission not found", 404)
        item = self.repo.get_permission_dependency(payload.permission_id, payload.depends_on_permission_id)
        if item is None:
            item = AdminPermissionDependency(
                permission_id=payload.permission_id,
                depends_on_permission_id=payload.depends_on_permission_id,
                status="active",
            )
        else:
            item.status = "active"
        saved = self.repo.save_permission_dependency(item)
        self._commit_and_refresh(saved)
        return saved

    def list_audit_tasks(
        self,
        page: PageParams,
        status: str | None = None,
        business_type: str | None = None,
        target_type: str | None = None,
        risk_level: str | None = None,
    ) -> tuple[list[AuditTask], int]:
        return self.repo.list_audit_tasks(page, status, business_type, target_type, risk_level)

    def create_audit_task(self, payload: AuditTaskCreateIn) -> AuditTask:
        task = AuditTask(**payload.model_dump(), status=AuditTaskStatus.pending.value)
        saved = self.repo.create_audit_task(task)
        self._commit_and_refresh(saved)
        return saved

    def claim_audit_task(self, task_id: int, reviewer_id: int) -> AuditTask:
        task = self._get_open_audit_task(task_id)
        before_data = self._audit_task_snapshot(task)
        self._transition_audit_task(task, AuditTaskStatus.processing.value)
        task.reviewer_id = reviewer_id
        after_data = self._audit_task_snapshot(task)
        self.repo.add_audit_record(
            AuditRecord(
                audit_task_id=task.id,
                reviewer_id=reviewer_id,
                action="claim",
                before_data=json.dumps(before_data, ensure_ascii=False),
                after_data=json.dumps(after_data, ensure_ascii=False),
                sync_status="skipped",
                sync_message="No business sync is required when claiming an audit task.",
            )
        )
        self._add_admin_operation_log(
            reviewer_id,
            "audit_task.claim",
            task.target_type,
            task.target_id,
            before_data,
            after_data,
        )
        self.db.add(task)
        self._commit_and_refresh(task)
        return task

    def decide_audit_task(self, task_id: int, reviewer_id: int, payload: AuditDecisionIn) -> AuditTask:
        task = self._get_open_audit_task(task_id)
        decision = payload.decision.value
        if decision not in self.allowed_decisions:
            raise AppException(ErrorCode.audit_invalid_status, "Invalid audit decision", 400)

        before_data = self._audit_task_snapshot(task)
        self._transition_audit_task(task, AuditTaskStatus.completed.value)
        task.decision = decision
        task.reason = payload.reason
        task.reviewer_id = reviewer_id
        task.reviewed_at = datetime.now(timezone.utc)
        sync_result = self._sync_audit_task_target(task)
        self.repo.add_audit_record(
            AuditRecord(
                audit_task_id=task.id,
                reviewer_id=reviewer_id,
                action=decision,
                reason=payload.reason,
                sync_status=str(sync_result["status"]),
                sync_message=str(sync_result["message"]) if sync_result["message"] is not None else None,
                before_data=json.dumps(before_data, ensure_ascii=False),
                after_data=json.dumps(self._audit_task_snapshot(task), ensure_ascii=False),
            )
        )
        self._add_admin_operation_log(
            reviewer_id,
            f"audit_task.{decision}",
            task.target_type,
            task.target_id,
            before_data,
            self._audit_task_snapshot(task),
        )
        self._add_audit_result_message(task)
        self.db.add(task)
        self._commit_and_refresh(task)
        return task

    def cancel_audit_task(self, task_id: int, reviewer_id: int, payload: AuditCancelIn) -> AuditTask:
        task = self._get_open_audit_task(task_id)
        before_data = self._audit_task_snapshot(task)
        self._transition_audit_task(task, AuditTaskStatus.canceled.value)
        task.reviewer_id = reviewer_id
        task.reason = payload.reason
        after_data = self._audit_task_snapshot(task)
        self.repo.add_audit_record(
            AuditRecord(
                audit_task_id=task.id,
                reviewer_id=reviewer_id,
                action="cancel",
                reason=payload.reason,
                before_data=json.dumps(before_data, ensure_ascii=False),
                after_data=json.dumps(after_data, ensure_ascii=False),
                sync_status="skipped",
                sync_message="No business sync is required when canceling an audit task.",
            )
        )
        self._add_admin_operation_log(
            reviewer_id,
            "audit_task.cancel",
            task.target_type,
            task.target_id,
            before_data,
            after_data,
        )
        self.db.add(task)
        self._commit_and_refresh(task)
        return task

    def list_audit_records(
        self,
        page: PageParams,
        audit_task_id: int | None = None,
        reviewer_id: int | None = None,
        action: str | None = None,
        sync_status: str | None = None,
    ) -> tuple[list[AuditRecord], int]:
        return self.repo.list_audit_records(page, audit_task_id, reviewer_id, action, sync_status)

    def list_risk_events(
        self,
        page: PageParams,
        status: str | None = None,
        event_type: str | None = None,
        risk_level: str | None = None,
    ) -> tuple[list[RiskEvent], int]:
        return self.repo.list_risk_events(page, status, event_type, risk_level)

    def create_risk_event(self, payload: RiskEventCreateIn) -> RiskEvent:
        event = self.repo.create_risk_event(RiskEvent(**payload.model_dump(), status="open"))
        self._commit_and_refresh(event)
        return event

    def list_risk_rules(
        self,
        page: PageParams,
        rule_type: str | None = None,
        enabled: bool | None = None,
    ) -> tuple[list[RiskRule], int]:
        return self.repo.list_risk_rules(page, rule_type, enabled)

    def create_risk_rule(self, payload: RiskRuleCreateIn) -> RiskRule:
        rule = self.repo.create_risk_rule(RiskRule(**payload.model_dump(), status="active"))
        self._commit_and_refresh(rule)
        return rule

    def list_report_cases(
        self,
        page: PageParams,
        status: str | None = None,
        target_type: str | None = None,
        reason_type: str | None = None,
    ) -> tuple[list[ReportCase], int]:
        return self.repo.list_report_cases(page, status, target_type, reason_type)

    def create_report_case(self, payload: ReportCaseCreateIn) -> ReportCase:
        report = self.repo.create_report_case(ReportCase(**payload.model_dump(), status="pending"))
        self._commit_and_refresh(report)
        return report

    def handle_report_case(self, report_id: int, handler_id: int, payload: ReportCaseHandleIn) -> ReportCase:
        report = self.repo.get_report_case(report_id)
        if report is None or report.deleted_at is not None:
            raise AppException(ErrorCode.not_found, "Report case not found", 404)
        before_data = self._report_case_snapshot(report)
        report.status = payload.status
        report.resolution_action = payload.resolution_action.value
        report.handle_reason = payload.reason
        report.handler_id = handler_id
        report.handled_at = datetime.now(timezone.utc)
        self._apply_report_resolution(report, handler_id, payload)
        self._add_admin_operation_log(
            handler_id,
            f"report_case.{payload.resolution_action.value}",
            report.target_type,
            report.target_id,
            before_data,
            self._report_case_snapshot(report),
        )
        saved = self.repo.save_report_case(report)
        self._commit_and_refresh(saved)
        return saved

    def list_blacklist(
        self,
        page: PageParams,
        target_type: str | None = None,
        status: str | None = None,
    ) -> tuple[list[Blacklist], int]:
        return self.repo.list_blacklist(page, target_type, status)

    def create_blacklist(self, payload: BlacklistCreateIn, operator_id: int) -> Blacklist:
        item = Blacklist(**payload.model_dump(), operator_id=operator_id, status="active")
        saved = self.repo.create_blacklist(item)
        self._add_admin_operation_log(
            operator_id,
            "blacklist.create",
            saved.target_type,
            saved.target_id,
            None,
            {
                "id": saved.id,
                "target_type": saved.target_type,
                "target_id": saved.target_id,
                "reason": saved.reason,
                "expires_at": saved.expires_at.isoformat() if saved.expires_at else None,
            },
        )
        self._commit_and_refresh(saved)
        return saved

    def list_messages(
        self,
        page: PageParams,
        receiver_id: int | None = None,
        is_read: bool | None = None,
        message_type: str | None = None,
    ) -> tuple[list[Message], int]:
        return self.repo.list_messages(page, receiver_id, is_read, message_type)

    def create_message(self, payload: MessageCreateIn) -> Message:
        message = self.repo.create_message(Message(**payload.model_dump(), is_read=False, status="sent"))
        self._commit_and_refresh(message)
        return message

    def mark_message_read(self, message_id: int, current_user_id: int) -> Message:
        message = self.repo.get_message(message_id)
        if message is None or message.deleted_at is not None:
            raise AppException(ErrorCode.not_found, "Message not found", 404)
        if message.receiver_id is not None and message.receiver_id != current_user_id:
            raise AppException(ErrorCode.forbidden, "No permission to read this message", 403)
        message.is_read = True
        message.read_at = datetime.now(timezone.utc)
        saved = self.repo.save_message(message)
        self._commit_and_refresh(saved)
        return saved

    def count_unread_messages(self, receiver_id: int | None = None) -> int:
        return self.repo.count_unread_messages(receiver_id)

    def list_message_templates(self, page: PageParams, status: str | None = None):
        return self.repo.list_message_templates(page, status)

    def create_message_template(self, payload: MessageTemplateCreateIn) -> MessageTemplate:
        template = self.repo.create_message_template(MessageTemplate(**payload.model_dump(), status="active"))
        self._commit_and_refresh(template)
        return template

    def render_message_template(self, template_id: int, payload_data: str | None = None) -> dict[str, str]:
        template = self.repo.get_message_template(template_id)
        if template is None or template.deleted_at is not None:
            raise AppException(ErrorCode.not_found, "Message template not found", 404)
        payload = self._parse_payload_data(payload_data)
        return {
            "title": self._render_template(template.title_template, payload),
            "content": self._render_template(template.content_template, payload),
        }

    def list_notification_tasks(
        self,
        page: PageParams,
        status: str | None = None,
        receiver_id: int | None = None,
    ) -> tuple[list[NotificationTask], int]:
        return self.repo.list_notification_tasks(page, status, receiver_id)

    def create_notification_task(self, payload: NotificationTaskCreateIn) -> NotificationTask:
        task = self.repo.create_notification_task(NotificationTask(**payload.model_dump(), status="pending"))
        self._commit_and_refresh(task)
        return task

    def update_notification_task_status(
        self,
        task_id: int,
        payload: NotificationTaskStatusIn,
    ) -> NotificationTask:
        task = self.repo.get_notification_task(task_id)
        if task is None or task.deleted_at is not None:
            raise AppException(ErrorCode.not_found, "Notification task not found", 404)
        self._transition_notification_task(task, payload.status.value, payload.reason)
        saved = self.repo.save_notification_task(task)
        self._commit_and_refresh(saved)
        return saved

    def send_notification_task(self, task_id: int) -> NotificationTask:
        task = self.repo.get_notification_task(task_id)
        if task is None or task.deleted_at is not None:
            raise AppException(ErrorCode.not_found, "Notification task not found", 404)
        self._transition_notification_task(task, "sending", None)
        if task.template_id is None:
            raise AppException(ErrorCode.not_found, "Notification template is required", 404)
        rendered = self.render_message_template(task.template_id, task.payload_data)
        self.repo.add_message(
            Message(
                receiver_id=task.receiver_id,
                message_type="notification",
                title=rendered["title"],
                content=rendered["content"],
                related_type="notification_task",
                related_id=str(task.id),
                is_read=False,
                status="sent",
            )
        )
        self._transition_notification_task(task, "sent", None)
        saved = self.repo.save_notification_task(task)
        self._commit_and_refresh(saved)
        return saved

    def list_configs(self, page: PageParams, config_type: str | None = None):
        return self.repo.list_configs(page, config_type)

    def upsert_config(self, payload: OperationConfigUpsertIn, operator_id: int) -> OperationConfig:
        config = self.repo.get_config_by_key(payload.config_key)
        normalized_value = self._normalize_config_value(payload.config_type, payload.config_value)
        before_data = None
        if config is None:
            config = OperationConfig(
                config_key=payload.config_key,
                config_value=normalized_value,
                config_type=payload.config_type.value,
                config_schema=payload.config_schema,
                description=payload.description,
                operator_id=operator_id,
                status="active",
            )
        else:
            before_data = {
                "config_key": config.config_key,
                "config_value": config.config_value,
                "config_type": config.config_type,
                "config_schema": config.config_schema,
                "description": config.description,
            }
            config.config_key = payload.config_key
            config.config_value = normalized_value
            config.config_type = payload.config_type.value
            config.config_schema = payload.config_schema
            config.description = payload.description
            config.operator_id = operator_id
        saved = self.repo.save_config(config)
        self._add_admin_operation_log(
            operator_id,
            "operation_config.upsert",
            "operation_config",
            saved.config_key,
            before_data,
            {
                "config_key": saved.config_key,
                "config_value": saved.config_value,
                "config_type": saved.config_type,
                "config_schema": saved.config_schema,
                "description": saved.description,
            },
        )
        self._commit_and_refresh(saved)
        return saved

    def create_statistics_snapshot(self, payload: StatisticsSnapshotCreateIn) -> StatisticsSnapshot:
        snapshot = self.repo.create_statistics_snapshot(StatisticsSnapshot(**payload.model_dump()))
        self._commit_and_refresh(snapshot)
        return snapshot

    def get_statistics_overview(self, snapshot_type: str = "daily") -> StatisticsSnapshot | None:
        return self.repo.get_latest_statistics_snapshot(snapshot_type)

    def create_data_event(self, payload: DataEventCreateIn) -> DataEvent:
        event = self.repo.create_data_event(DataEvent(**payload.model_dump()))
        self._commit_and_refresh(event)
        return event

    def list_data_events(
        self,
        page: PageParams,
        event_type: str | None = None,
        source: str | None = None,
    ) -> tuple[list[DataEvent], int]:
        return self.repo.list_data_events(page, event_type, source)

    def aggregate_statistics_snapshot(self, payload: StatisticsAggregateIn) -> StatisticsSnapshot:
        metric_values = {
            metric_name: self.repo.count_data_events(event_type, payload.metric_date)
            for metric_name, event_type in self.statistic_event_map.items()
        }
        metric_values["active_users"] = self.repo.count_distinct_event_users("user_active", payload.metric_date)
        snapshot = StatisticsSnapshot(
            snapshot_type=payload.snapshot_type,
            metric_date=payload.metric_date,
            gmv_cent=0,
            extra_data=json.dumps({"source": "data_event"}, ensure_ascii=False),
            **metric_values,
        )
        saved = self.repo.create_statistics_snapshot(snapshot)
        self._commit_and_refresh(saved)
        return saved

    def get_release_checklist(self) -> dict[str, list[str]]:
        return {
            "p0_test_cases": [
                "Admin can create audit tasks and complete approve/reject/takedown/ban/request_changes decisions.",
                "Report handling can close, warn, blacklist, ban, takedown, and notify target users.",
                "Notification tasks render templates and flow through pending, sending, sent, failed, canceled.",
                "RBAC assignment auto-grants permission dependencies for role permissions.",
            ],
            "integration_checklist": [
                "A submits user/auth data to audit_task and consumes audit_record sync result.",
                "B submits order/payment/after-sale data_event for statistics aggregation.",
                "C submits merchant/product/pet/adoption/community objects to audit_task.",
                "Message unread count and message list are verified for user and admin roles.",
            ],
            "defect_levels": [
                "P0: audit decision lost, permission bypass, message delivery failure for critical flows.",
                "P1: statistics mismatch, report action missing notification, blacklist expiration wrong.",
                "P2: filtering, copy, or non-critical operation log field issues.",
            ],
            "release_gate": [
                "Alembic migration applies and rolls back on a fresh database.",
                "OpenAPI contains admin-audit, risk, report, message, config, statistics endpoints.",
                "P0 tests pass and smoke tests cover login, RBAC, audit, report, message, statistics.",
            ],
            "rollback_plan": [
                "Stop writing new audit_task, notification_task, and data_event records.",
                "Run Alembic downgrade for the admin-audit revision if data preservation is not required.",
                "Restore previous API image and replay failed notification tasks after recovery.",
            ],
        }

    def _apply_report_resolution(
        self,
        report: ReportCase,
        handler_id: int,
        payload: ReportCaseHandleIn,
    ) -> None:
        action = payload.resolution_action.value
        if action in {"ban", "blacklist"}:
            self.repo.add_blacklist(
                Blacklist(
                    target_type=report.target_type,
                    target_id=report.target_id,
                    reason=payload.reason or report.reason_type,
                    operator_id=handler_id,
                    expires_at=payload.blacklist_expires_at,
                    status="active",
                )
            )
        if action == "takedown":
            self.db.add(
                RiskEvent(
                    event_type="report_takedown",
                    target_type=report.target_type,
                    target_id=report.target_id,
                    user_id=payload.notify_receiver_id,
                    risk_level="high",
                    description=payload.reason or report.description,
                    status="handled",
                )
            )
        receiver_id = payload.notify_receiver_id or report.reporter_id
        if receiver_id is not None:
            self.repo.add_message(
                Message(
                    receiver_id=receiver_id,
                    message_type="report_result",
                    title="Report handled",
                    content=payload.reason or f"Your report has been handled with action: {action}.",
                    related_type=report.target_type,
                    related_id=report.target_id,
                    is_read=False,
                    status="sent",
                )
            )

    def _transition_notification_task(
        self,
        task: NotificationTask,
        next_status: str,
        reason: str | None,
    ) -> None:
        allowed_next_statuses = self.notification_status_flow.get(task.status, set())
        if next_status not in allowed_next_statuses:
            raise AppException(
                ErrorCode.audit_invalid_status,
                f"Cannot change notification task status from {task.status} to {next_status}",
                400,
            )
        task.status = next_status
        task.status_reason = reason
        if next_status == "sent":
            task.sent_at = datetime.now(timezone.utc)

    def _parse_payload_data(self, payload_data: str | None) -> dict[str, object]:
        if not payload_data:
            return {}
        try:
            data = json.loads(payload_data)
        except json.JSONDecodeError as exc:
            raise AppException(ErrorCode.audit_invalid_status, "Invalid notification payload JSON", 400) from exc
        if not isinstance(data, dict):
            raise AppException(ErrorCode.audit_invalid_status, "Notification payload must be a JSON object", 400)
        return data

    def _render_template(self, template: str, payload: dict[str, object]) -> str:
        rendered = template
        for key, value in payload.items():
            rendered = rendered.replace("{{" + key + "}}", str(value))
        return rendered

    def _normalize_config_value(self, config_type: OperationConfigType, value: object) -> str:
        if config_type == OperationConfigType.text:
            return str(value)
        if config_type == OperationConfigType.number:
            if not isinstance(value, int | float) or isinstance(value, bool):
                raise AppException(ErrorCode.audit_invalid_status, "number config_value must be numeric", 400)
            return json.dumps(value, ensure_ascii=False)
        if config_type == OperationConfigType.boolean:
            if not isinstance(value, bool):
                raise AppException(ErrorCode.audit_invalid_status, "boolean config_value must be boolean", 400)
            return json.dumps(value, ensure_ascii=False)
        if config_type == OperationConfigType.list:
            if not isinstance(value, list):
                raise AppException(ErrorCode.audit_invalid_status, "list config_value must be a list", 400)
            return json.dumps(value, ensure_ascii=False)
        if config_type == OperationConfigType.object:
            if not isinstance(value, dict):
                raise AppException(ErrorCode.audit_invalid_status, "object config_value must be an object", 400)
            return json.dumps(value, ensure_ascii=False)
        return json.dumps(value, ensure_ascii=False)

    def _get_open_audit_task(self, task_id: int) -> AuditTask:
        task = self.repo.get_audit_task(task_id)
        if task is None or task.deleted_at is not None:
            raise AppException(ErrorCode.audit_not_found, "Audit task not found", 404)
        if task.status in self.terminal_audit_statuses:
            raise AppException(ErrorCode.audit_already_reviewed, "Audit task has reached a terminal status", 409)
        return task

    def _transition_audit_task(self, task: AuditTask, next_status: str) -> None:
        allowed_next_statuses = self.audit_status_flow.get(task.status, set())
        if next_status not in allowed_next_statuses:
            raise AppException(
                ErrorCode.audit_invalid_status,
                f"Cannot change audit task status from {task.status} to {next_status}",
                400,
            )
        task.status = next_status

    def _sync_audit_task_target(self, task: AuditTask) -> dict[str, object | None]:
        target_status = self.sync_status_map.get(task.target_type, {}).get(task.decision or "")
        if target_status is None:
            return {
                "status": "skipped",
                "message": f"No sync rule for target_type={task.target_type}, decision={task.decision}.",
            }

        if task.target_type != "real_name_auth":
            return {
                "status": "skipped",
                "message": f"No sync adapter implemented for target_type={task.target_type}.",
            }

        try:
            target_id = int(task.target_id)
        except ValueError as exc:
            raise AppException(ErrorCode.audit_invalid_status, "Invalid audit target id", 400) from exc

        real_name_auth = self.db.get(RealNameAuth, target_id)
        if real_name_auth is None or real_name_auth.deleted_at is not None:
            raise AppException(ErrorCode.not_found, "Real name auth record not found", 404)

        real_name_auth.status = target_status
        real_name_auth.audit_reason = task.reason

        user = self.db.get(User, real_name_auth.user_id)
        if user is not None:
            user.real_name_status = target_status
            self.db.add(user)
        self.db.add(real_name_auth)
        return {
            "status": "synced",
            "message": f"Synced real_name_auth and user real_name_status to {target_status}.",
        }

    def _add_admin_operation_log(
        self,
        operator_id: int,
        action: str,
        target_type: str | None,
        target_id: str | None,
        before_data: dict[str, object] | None,
        after_data: dict[str, object] | None,
    ) -> None:
        self.db.add(
            OperationLog(
                operator_id=operator_id,
                operator_type="admin",
                action=action,
                target_type=target_type,
                target_id=target_id,
                before_data=json.dumps(before_data, ensure_ascii=False) if before_data is not None else None,
                after_data=json.dumps(after_data, ensure_ascii=False) if after_data is not None else None,
            )
        )

    def _add_audit_result_message(self, task: AuditTask) -> None:
        if task.submitter_id is None:
            return
        self.db.add(
            Message(
                receiver_id=task.submitter_id,
                message_type="audit_result",
                title=f"Audit result: {task.title}",
                content=task.reason or f"Your submission has been {task.decision}.",
                related_type=task.target_type,
                related_id=task.target_id,
                is_read=False,
                status="sent",
            )
        )

    def _audit_task_snapshot(self, task: AuditTask) -> dict[str, object]:
        return {
            "id": task.id,
            "business_type": task.business_type,
            "target_type": task.target_type,
            "target_id": task.target_id,
            "status": task.status,
            "decision": task.decision,
            "reason": task.reason,
            "reviewer_id": task.reviewer_id,
            "reviewed_at": task.reviewed_at.isoformat() if task.reviewed_at else None,
        }

    def _report_case_snapshot(self, report: ReportCase) -> dict[str, object]:
        return {
            "id": report.id,
            "target_type": report.target_type,
            "target_id": report.target_id,
            "reason_type": report.reason_type,
            "status": report.status,
            "resolution_action": report.resolution_action,
            "handle_reason": report.handle_reason,
            "handler_id": report.handler_id,
            "handled_at": report.handled_at.isoformat() if report.handled_at else None,
        }
