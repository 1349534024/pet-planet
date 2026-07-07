import itertools

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.deps import get_db
from app.core.security import create_access_token
from app.db.base import Base
from app.main import app
from app.models import admin_audit, file, operation_log, pet, user  # noqa: F401
from app.models.admin_audit import (
    AdminPermission,
    AdminRole,
    AdminRolePermission,
    AdminUser,
    AdminUserRole,
    AuditRecord,
    AuditTask,
    Blacklist,
    Message,
    NotificationTask,
    ReportCase,
)
from app.models.operation_log import OperationLog
from app.models.user import Role, User


_user_counter = itertools.count(1)


@pytest.fixture()
def client_and_db():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as client:
            yield client, TestingSessionLocal
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=engine)


def _create_user(SessionLocal, role_code: str = "admin") -> tuple[int, dict[str, str]]:
    db = SessionLocal()
    try:
        role = Role(code=role_code, name=role_code)
        user_obj = User(phone=f"188{next(_user_counter):08d}", nickname=role_code, status="active")
        user_obj.roles.append(role)
        db.add_all([role, user_obj])
        db.commit()
        db.refresh(user_obj)
        token = create_access_token(str(user_obj.id), {"roles": [role_code]})
        return user_obj.id, {"Authorization": f"Bearer {token}"}
    finally:
        db.close()


def _create_admin_with_permissions(
    SessionLocal,
    permission_codes: list[str],
    role_code: str = "admin_audit_role",
) -> tuple[int, dict[str, str]]:
    user_id, headers = _create_user(SessionLocal, f"user_{role_code[:4]}")
    db = SessionLocal()
    try:
        admin_user_obj = AdminUser(user_id=user_id, username=f"admin_{user_id}", status="active")
        admin_role_obj = AdminRole(code=f"{role_code}_{user_id}", name=role_code, status="active")
        db.add_all([admin_user_obj, admin_role_obj])
        db.flush()
        db.add(AdminUserRole(admin_user_id=admin_user_obj.id, role_id=admin_role_obj.id, status="active"))
        for code in permission_codes:
            permission = AdminPermission(code=code, name=code, module=code.split(":")[0], status="active")
            db.add(permission)
            db.flush()
            db.add(AdminRolePermission(role_id=admin_role_obj.id, permission_id=permission.id, status="active"))
        db.commit()
        return user_id, headers
    finally:
        db.close()


def test_rbac_requires_login_and_admin_permission(client_and_db):
    client, SessionLocal = client_and_db
    _, user_headers = _create_user(SessionLocal, "user")
    _, audit_read_headers = _create_admin_with_permissions(SessionLocal, ["audit:read"], "audit_reader")

    assert client.get("/api/v1/admin/audit/tasks").status_code == 401
    assert client.get("/api/v1/admin/audit/tasks", headers=user_headers).status_code == 403

    response = client.get("/api/v1/admin/audit/tasks", headers=audit_read_headers)
    assert response.status_code == 200
    assert response.json()["code"] == "SUCCESS"


def test_user_with_audit_decision_permission_can_review(client_and_db):
    client, SessionLocal = client_and_db
    reviewer_id, headers = _create_admin_with_permissions(SessionLocal, ["audit:decision"], "audit_decider")
    db = SessionLocal()
    try:
        task = AuditTask(
            business_type="product",
            target_type="product",
            target_id="P2001",
            reviewer_id=None,
            title="Decision-only audit",
            risk_level="low",
            status="pending",
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        task_id = task.id
    finally:
        db.close()

    response = client.post(
        f"/api/v1/admin/audit/{task_id}/decision",
        headers=headers,
        json={"decision": "approve", "reason": "Decision permission is enough"},
    )
    assert response.status_code == 200
    assert response.json()["data"]["reviewer_id"] == reviewer_id
    assert response.json()["data"]["status"] == "completed"


def test_audit_task_claim_decision_and_records(client_and_db):
    client, SessionLocal = client_and_db
    _, headers = _create_admin_with_permissions(
        SessionLocal,
        ["audit:read", "audit:claim", "audit:decision"],
        "audit_operator",
    )

    create_response = client.post(
        "/api/v1/admin/audit/tasks",
        headers=headers,
        json={
            "business_type": "product",
            "target_type": "product",
            "target_id": "P1001",
            "title": "Product publish audit",
            "risk_level": "medium",
        },
    )
    assert create_response.status_code == 200
    task_id = create_response.json()["data"]["id"]

    claim_response = client.post(f"/api/v1/admin/audit/{task_id}/claim", headers=headers)
    assert claim_response.status_code == 200
    assert claim_response.json()["data"]["status"] == "processing"

    decision_response = client.post(
        f"/api/v1/admin/audit/{task_id}/decision",
        headers=headers,
        json={"decision": "approve", "reason": "Looks good"},
    )
    assert decision_response.status_code == 200
    assert decision_response.json()["data"]["status"] == "completed"

    records_response = client.get(f"/api/v1/admin/audit/records?audit_task_id={task_id}", headers=headers)
    assert records_response.status_code == 200
    actions = {item["action"] for item in records_response.json()["data"]["items"]}
    assert {"claim", "approve"}.issubset(actions)

    db = SessionLocal()
    try:
        records = db.scalars(select(AuditRecord).where(AuditRecord.audit_task_id == task_id)).all()
        assert len(records) == 2
    finally:
        db.close()


def test_report_handle_blacklist_creates_message_and_operation_log(client_and_db):
    client, SessionLocal = client_and_db
    reporter_id, headers = _create_admin_with_permissions(SessionLocal, ["risk:write"], "risk_handler")

    report_response = client.post(
        "/api/v1/admin/reports",
        headers=headers,
        json={
            "target_type": "user",
            "target_id": "bad-user",
            "reason_type": "fraud",
            "description": "Private transaction scam",
        },
    )
    assert report_response.status_code == 200
    report_id = report_response.json()["data"]["id"]

    handle_response = client.post(
        f"/api/v1/admin/reports/{report_id}/handle",
        headers=headers,
        json={
            "status": "handled",
            "resolution_action": "blacklist",
            "reason": "Confirmed fraud",
            "notify_receiver_id": reporter_id,
        },
    )
    assert handle_response.status_code == 200
    assert handle_response.json()["data"]["resolution_action"] == "blacklist"

    db = SessionLocal()
    try:
        report = db.get(ReportCase, report_id)
        blacklist = db.scalar(select(Blacklist).where(Blacklist.target_id == "bad-user"))
        message = db.scalar(select(Message).where(Message.message_type == "report_result"))
        log = db.scalar(select(OperationLog).where(OperationLog.action == "report_case.blacklist"))
        assert report.status == "handled"
        assert blacklist is not None
        assert message is not None
        assert log is not None
    finally:
        db.close()


def test_create_blacklist_writes_operation_log_atomically(client_and_db):
    client, SessionLocal = client_and_db
    _, headers = _create_admin_with_permissions(SessionLocal, ["risk:write"], "risk_writer")

    response = client.post(
        "/api/v1/admin/blacklist",
        headers=headers,
        json={"target_type": "user", "target_id": "U9001", "reason": "Abuse"},
    )
    assert response.status_code == 200

    db = SessionLocal()
    try:
        blacklist = db.scalar(select(Blacklist).where(Blacklist.target_id == "U9001"))
        log = db.scalar(select(OperationLog).where(OperationLog.action == "blacklist.create"))
        assert blacklist is not None
        assert log is not None
        assert log.target_id == "U9001"
    finally:
        db.close()


def test_notification_template_render_and_send_creates_message(client_and_db):
    client, SessionLocal = client_and_db
    receiver_id, headers = _create_admin_with_permissions(
        SessionLocal,
        ["message:read", "message:write"],
        "message_operator",
    )

    template_response = client.post(
        "/api/v1/admin/message-templates",
        headers=headers,
        json={
            "code": "audit_notice",
            "name": "Audit notice",
            "title_template": "Hello {{name}}",
            "content_template": "Your {{target}} was approved.",
        },
    )
    assert template_response.status_code == 200
    template_id = template_response.json()["data"]["id"]

    render_response = client.post(
        f"/api/v1/admin/message-templates/{template_id}/render",
        headers=headers,
        params={"payload_data": '{"name":"Ada","target":"product"}'},
    )
    assert render_response.status_code == 200
    assert render_response.json()["data"]["title"] == "Hello Ada"

    task_response = client.post(
        "/api/v1/admin/notifications",
        headers=headers,
        json={
            "template_id": template_id,
            "receiver_id": receiver_id,
            "channel": "in_app",
            "payload_data": '{"name":"Ada","target":"product"}',
        },
    )
    assert task_response.status_code == 200
    task_id = task_response.json()["data"]["id"]

    send_response = client.post(f"/api/v1/admin/notifications/{task_id}/send", headers=headers)
    assert send_response.status_code == 200
    assert send_response.json()["data"]["status"] == "sent"

    db = SessionLocal()
    try:
        task = db.get(NotificationTask, task_id)
        message = db.scalar(select(Message).where(Message.related_id == str(task_id)))
        assert task.status == "sent"
        assert message.title == "Hello Ada"
        assert message.content == "Your product was approved."
    finally:
        db.close()
