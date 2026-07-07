from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.pagination import PageParams
from app.models.admin_audit import (
    AdminPermission,
    AdminPermissionDependency,
    AdminRolePermission,
    AdminRole,
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


class AdminAuditRepository:
    def __init__(self, db: Session):
        self.db = db

    def _stage(self, item):
        self.db.add(item)
        self.db.flush()
        return item

    def get_audit_task(self, task_id: int) -> AuditTask | None:
        return self.db.get(AuditTask, task_id)

    def list_admin_users(self, page: PageParams, status: str | None = None) -> tuple[list[AdminUser], int]:
        stmt = select(AdminUser).where(AdminUser.deleted_at.is_(None))
        if status:
            stmt = stmt.where(AdminUser.status == status)
        total = self.db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
        items = list(self.db.scalars(stmt.order_by(AdminUser.id.desc()).offset(page.offset).limit(page.page_size)))
        return items, total

    def create_admin_user(self, admin_user: AdminUser) -> AdminUser:
        return self._stage(admin_user)

    def list_admin_roles(self, page: PageParams, status: str | None = None) -> tuple[list[AdminRole], int]:
        stmt = select(AdminRole).where(AdminRole.deleted_at.is_(None))
        if status:
            stmt = stmt.where(AdminRole.status == status)
        total = self.db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
        items = list(self.db.scalars(stmt.order_by(AdminRole.id.desc()).offset(page.offset).limit(page.page_size)))
        return items, total

    def create_admin_role(self, role: AdminRole) -> AdminRole:
        return self._stage(role)

    def list_admin_permissions(
        self,
        page: PageParams,
        module: str | None = None,
        status: str | None = None,
    ) -> tuple[list[AdminPermission], int]:
        stmt = select(AdminPermission).where(AdminPermission.deleted_at.is_(None))
        if module:
            stmt = stmt.where(AdminPermission.module == module)
        if status:
            stmt = stmt.where(AdminPermission.status == status)
        total = self.db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
        items = list(self.db.scalars(stmt.order_by(AdminPermission.id.desc()).offset(page.offset).limit(page.page_size)))
        return items, total

    def create_admin_permission(self, permission: AdminPermission) -> AdminPermission:
        return self._stage(permission)

    def get_admin_user(self, admin_user_id: int) -> AdminUser | None:
        return self.db.get(AdminUser, admin_user_id)

    def get_admin_role(self, role_id: int) -> AdminRole | None:
        return self.db.get(AdminRole, role_id)

    def get_admin_permission(self, permission_id: int) -> AdminPermission | None:
        return self.db.get(AdminPermission, permission_id)

    def get_admin_user_role(self, admin_user_id: int, role_id: int) -> AdminUserRole | None:
        return self.db.scalar(
            select(AdminUserRole).where(
                AdminUserRole.admin_user_id == admin_user_id,
                AdminUserRole.role_id == role_id,
                AdminUserRole.deleted_at.is_(None),
            )
        )

    def save_admin_user_role(self, item: AdminUserRole) -> AdminUserRole:
        return self._stage(item)

    def list_admin_user_roles(self, admin_user_id: int) -> list[AdminUserRole]:
        return list(
            self.db.scalars(
                select(AdminUserRole)
                .where(AdminUserRole.admin_user_id == admin_user_id, AdminUserRole.deleted_at.is_(None))
                .order_by(AdminUserRole.id.desc())
            )
        )

    def get_admin_role_permission(self, role_id: int, permission_id: int) -> AdminRolePermission | None:
        return self.db.scalar(
            select(AdminRolePermission).where(
                AdminRolePermission.role_id == role_id,
                AdminRolePermission.permission_id == permission_id,
                AdminRolePermission.deleted_at.is_(None),
            )
        )

    def save_admin_role_permission(self, item: AdminRolePermission) -> AdminRolePermission:
        return self._stage(item)

    def list_admin_role_permissions(self, role_id: int) -> list[AdminRolePermission]:
        return list(
            self.db.scalars(
                select(AdminRolePermission)
                .where(AdminRolePermission.role_id == role_id, AdminRolePermission.deleted_at.is_(None))
                .order_by(AdminRolePermission.id.desc())
            )
        )

    def list_permission_dependencies(self, permission_id: int) -> list[AdminPermissionDependency]:
        return list(
            self.db.scalars(
                select(AdminPermissionDependency)
                .where(
                    AdminPermissionDependency.permission_id == permission_id,
                    AdminPermissionDependency.deleted_at.is_(None),
                )
                .order_by(AdminPermissionDependency.id.desc())
            )
        )

    def get_permission_dependency(
        self,
        permission_id: int,
        depends_on_permission_id: int,
    ) -> AdminPermissionDependency | None:
        return self.db.scalar(
            select(AdminPermissionDependency).where(
                AdminPermissionDependency.permission_id == permission_id,
                AdminPermissionDependency.depends_on_permission_id == depends_on_permission_id,
                AdminPermissionDependency.deleted_at.is_(None),
            )
        )

    def save_permission_dependency(self, item: AdminPermissionDependency) -> AdminPermissionDependency:
        return self._stage(item)

    def list_audit_tasks(
        self,
        page: PageParams,
        status: str | None = None,
        business_type: str | None = None,
        target_type: str | None = None,
        risk_level: str | None = None,
    ) -> tuple[list[AuditTask], int]:
        stmt = select(AuditTask).where(AuditTask.deleted_at.is_(None))
        if status:
            stmt = stmt.where(AuditTask.status == status)
        if business_type:
            stmt = stmt.where(AuditTask.business_type == business_type)
        if target_type:
            stmt = stmt.where(AuditTask.target_type == target_type)
        if risk_level:
            stmt = stmt.where(AuditTask.risk_level == risk_level)
        total = self.db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
        items = list(self.db.scalars(stmt.order_by(AuditTask.id.desc()).offset(page.offset).limit(page.page_size)))
        return items, total

    def create_audit_task(self, task: AuditTask) -> AuditTask:
        return self._stage(task)

    def save_audit_task(self, task: AuditTask) -> AuditTask:
        return self._stage(task)

    def add_audit_record(self, record: AuditRecord) -> None:
        self.db.add(record)

    def list_audit_records(
        self,
        page: PageParams,
        audit_task_id: int | None = None,
        reviewer_id: int | None = None,
        action: str | None = None,
        sync_status: str | None = None,
    ) -> tuple[list[AuditRecord], int]:
        stmt = select(AuditRecord).where(AuditRecord.deleted_at.is_(None))
        if audit_task_id is not None:
            stmt = stmt.where(AuditRecord.audit_task_id == audit_task_id)
        if reviewer_id is not None:
            stmt = stmt.where(AuditRecord.reviewer_id == reviewer_id)
        if action:
            stmt = stmt.where(AuditRecord.action == action)
        if sync_status:
            stmt = stmt.where(AuditRecord.sync_status == sync_status)
        total = self.db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
        items = list(self.db.scalars(stmt.order_by(AuditRecord.id.desc()).offset(page.offset).limit(page.page_size)))
        return items, total

    def list_risk_events(
        self,
        page: PageParams,
        status: str | None = None,
        event_type: str | None = None,
        risk_level: str | None = None,
    ) -> tuple[list[RiskEvent], int]:
        stmt = select(RiskEvent).where(RiskEvent.deleted_at.is_(None))
        if status:
            stmt = stmt.where(RiskEvent.status == status)
        if event_type:
            stmt = stmt.where(RiskEvent.event_type == event_type)
        if risk_level:
            stmt = stmt.where(RiskEvent.risk_level == risk_level)
        total = self.db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
        items = list(self.db.scalars(stmt.order_by(RiskEvent.id.desc()).offset(page.offset).limit(page.page_size)))
        return items, total

    def create_risk_event(self, event: RiskEvent) -> RiskEvent:
        return self._stage(event)

    def list_risk_rules(
        self,
        page: PageParams,
        rule_type: str | None = None,
        enabled: bool | None = None,
    ) -> tuple[list[RiskRule], int]:
        stmt = select(RiskRule).where(RiskRule.deleted_at.is_(None))
        if rule_type:
            stmt = stmt.where(RiskRule.rule_type == rule_type)
        if enabled is not None:
            stmt = stmt.where(RiskRule.enabled == enabled)
        total = self.db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
        items = list(self.db.scalars(stmt.order_by(RiskRule.id.desc()).offset(page.offset).limit(page.page_size)))
        return items, total

    def create_risk_rule(self, rule: RiskRule) -> RiskRule:
        return self._stage(rule)

    def list_report_cases(
        self,
        page: PageParams,
        status: str | None = None,
        target_type: str | None = None,
        reason_type: str | None = None,
    ) -> tuple[list[ReportCase], int]:
        stmt = select(ReportCase).where(ReportCase.deleted_at.is_(None))
        if status:
            stmt = stmt.where(ReportCase.status == status)
        if target_type:
            stmt = stmt.where(ReportCase.target_type == target_type)
        if reason_type:
            stmt = stmt.where(ReportCase.reason_type == reason_type)
        total = self.db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
        items = list(self.db.scalars(stmt.order_by(ReportCase.id.desc()).offset(page.offset).limit(page.page_size)))
        return items, total

    def get_report_case(self, report_id: int) -> ReportCase | None:
        return self.db.get(ReportCase, report_id)

    def create_report_case(self, report: ReportCase) -> ReportCase:
        return self._stage(report)

    def save_report_case(self, report: ReportCase) -> ReportCase:
        return self._stage(report)

    def list_blacklist(
        self,
        page: PageParams,
        target_type: str | None = None,
        status: str | None = None,
    ) -> tuple[list[Blacklist], int]:
        stmt = select(Blacklist).where(Blacklist.deleted_at.is_(None))
        if target_type:
            stmt = stmt.where(Blacklist.target_type == target_type)
        if status:
            stmt = stmt.where(Blacklist.status == status)
        total = self.db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
        items = list(self.db.scalars(stmt.order_by(Blacklist.id.desc()).offset(page.offset).limit(page.page_size)))
        return items, total

    def create_blacklist(self, item: Blacklist) -> Blacklist:
        return self._stage(item)

    def add_blacklist(self, item: Blacklist) -> Blacklist:
        self.db.add(item)
        return item

    def list_messages(
        self,
        page: PageParams,
        receiver_id: int | None = None,
        is_read: bool | None = None,
        message_type: str | None = None,
    ) -> tuple[list[Message], int]:
        stmt = select(Message).where(Message.deleted_at.is_(None))
        if receiver_id is not None:
            stmt = stmt.where(Message.receiver_id == receiver_id)
        if is_read is not None:
            stmt = stmt.where(Message.is_read == is_read)
        if message_type:
            stmt = stmt.where(Message.message_type == message_type)
        total = self.db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
        items = list(self.db.scalars(stmt.order_by(Message.id.desc()).offset(page.offset).limit(page.page_size)))
        return items, total

    def get_message(self, message_id: int) -> Message | None:
        return self.db.get(Message, message_id)

    def create_message(self, message: Message) -> Message:
        return self._stage(message)

    def add_message(self, message: Message) -> Message:
        self.db.add(message)
        return message

    def save_message(self, message: Message) -> Message:
        return self._stage(message)

    def count_unread_messages(self, receiver_id: int | None = None) -> int:
        stmt = select(func.count()).select_from(Message).where(Message.deleted_at.is_(None), Message.is_read.is_(False))
        if receiver_id is not None:
            stmt = stmt.where(Message.receiver_id == receiver_id)
        return self.db.scalar(stmt) or 0

    def list_message_templates(
        self,
        page: PageParams,
        status: str | None = None,
    ) -> tuple[list[MessageTemplate], int]:
        stmt = select(MessageTemplate).where(MessageTemplate.deleted_at.is_(None))
        if status:
            stmt = stmt.where(MessageTemplate.status == status)
        total = self.db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
        items = list(
            self.db.scalars(stmt.order_by(MessageTemplate.id.desc()).offset(page.offset).limit(page.page_size))
        )
        return items, total

    def create_message_template(self, template: MessageTemplate) -> MessageTemplate:
        return self._stage(template)

    def get_message_template(self, template_id: int) -> MessageTemplate | None:
        return self.db.get(MessageTemplate, template_id)

    def list_notification_tasks(
        self,
        page: PageParams,
        status: str | None = None,
        receiver_id: int | None = None,
    ) -> tuple[list[NotificationTask], int]:
        stmt = select(NotificationTask).where(NotificationTask.deleted_at.is_(None))
        if status:
            stmt = stmt.where(NotificationTask.status == status)
        if receiver_id is not None:
            stmt = stmt.where(NotificationTask.receiver_id == receiver_id)
        total = self.db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
        items = list(
            self.db.scalars(stmt.order_by(NotificationTask.id.desc()).offset(page.offset).limit(page.page_size))
        )
        return items, total

    def create_notification_task(self, task: NotificationTask) -> NotificationTask:
        return self._stage(task)

    def get_notification_task(self, task_id: int) -> NotificationTask | None:
        return self.db.get(NotificationTask, task_id)

    def save_notification_task(self, task: NotificationTask) -> NotificationTask:
        return self._stage(task)

    def list_configs(self, page: PageParams, config_type: str | None = None) -> tuple[list[OperationConfig], int]:
        stmt = select(OperationConfig).where(OperationConfig.deleted_at.is_(None))
        if config_type:
            stmt = stmt.where(OperationConfig.config_type == config_type)
        total = self.db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
        items = list(self.db.scalars(stmt.order_by(OperationConfig.id.desc()).offset(page.offset).limit(page.page_size)))
        return items, total

    def get_config_by_key(self, config_key: str) -> OperationConfig | None:
        return self.db.scalar(
            select(OperationConfig).where(
                OperationConfig.config_key == config_key,
                OperationConfig.deleted_at.is_(None),
            )
        )

    def save_config(self, config: OperationConfig) -> OperationConfig:
        return self._stage(config)

    def create_statistics_snapshot(self, snapshot: StatisticsSnapshot) -> StatisticsSnapshot:
        return self._stage(snapshot)

    def get_latest_statistics_snapshot(self, snapshot_type: str = "daily") -> StatisticsSnapshot | None:
        return self.db.scalar(
            select(StatisticsSnapshot)
            .where(StatisticsSnapshot.snapshot_type == snapshot_type, StatisticsSnapshot.deleted_at.is_(None))
            .order_by(StatisticsSnapshot.metric_date.desc(), StatisticsSnapshot.id.desc())
        )

    def create_data_event(self, event: DataEvent) -> DataEvent:
        return self._stage(event)

    def list_data_events(
        self,
        page: PageParams,
        event_type: str | None = None,
        source: str | None = None,
    ) -> tuple[list[DataEvent], int]:
        stmt = select(DataEvent).where(DataEvent.deleted_at.is_(None))
        if event_type:
            stmt = stmt.where(DataEvent.event_type == event_type)
        if source:
            stmt = stmt.where(DataEvent.source == source)
        total = self.db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
        items = list(self.db.scalars(stmt.order_by(DataEvent.id.desc()).offset(page.offset).limit(page.page_size)))
        return items, total

    def count_data_events(self, event_type: str, metric_date: str) -> int:
        return (
            self.db.scalar(
                select(func.count())
                .select_from(DataEvent)
                .where(
                    DataEvent.event_type == event_type,
                    DataEvent.deleted_at.is_(None),
                    func.substr(DataEvent.created_at, 1, 10) == metric_date,
                )
            )
            or 0
        )

    def count_distinct_event_users(self, event_type: str, metric_date: str) -> int:
        return (
            self.db.scalar(
                select(func.count(func.distinct(DataEvent.user_id)))
                .select_from(DataEvent)
                .where(
                    DataEvent.event_type == event_type,
                    DataEvent.user_id.is_not(None),
                    DataEvent.deleted_at.is_(None),
                    func.substr(DataEvent.created_at, 1, 10) == metric_date,
                )
            )
            or 0
        )
