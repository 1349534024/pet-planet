from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.deps import get_db
from app.core.permissions import RoleCode
from app.db.base import Base
from app.main import app
from app.models import file, operation_log, pet, user  # noqa: F401
from app.repositories.user_repo import UserRepository


@pytest.fixture()
def client() -> Generator[TestClient, None, None]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    Base.metadata.create_all(bind=engine)

    def override_get_db() -> Generator[Session, None, None]:
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


def login_by_sms(client: TestClient, phone: str) -> dict:
    response = client.post("/api/v1/auth/login/sms", json={"phone": phone, "code": "123456"})
    assert response.status_code == 200
    return response.json()["data"]


def grant_roles(role_codes: list[str], user_id: int) -> None:
    override_get_db = app.dependency_overrides[get_db]
    db = next(override_get_db())
    try:
        repo = UserRepository(db)
        repo.ensure_default_roles()
        user = repo.get_by_id(user_id)
        assert user is not None
        repo.set_user_roles(user, repo.get_roles_by_codes(role_codes))
    finally:
        db.close()


def test_user_can_view_own_roles(client: TestClient):
    login_data = login_by_sms(client, "13800001000")

    response = client.get(
        "/api/v1/roles/me",
        headers={"Authorization": f"Bearer {login_data['access_token']}"},
    )

    assert response.status_code == 200
    role_codes = [role["code"] for role in response.json()["data"]["roles"]]
    assert role_codes == [RoleCode.user.value]


def test_normal_user_cannot_manage_roles(client: TestClient):
    login_data = login_by_sms(client, "13800001001")

    response = client.get(
        "/api/v1/roles",
        headers={"Authorization": f"Bearer {login_data['access_token']}"},
    )

    assert response.status_code == 403
    assert response.json()["code"] == "FORBIDDEN"


def test_admin_can_list_and_assign_roles(client: TestClient):
    admin_login = login_by_sms(client, "13800001002")
    target_login = login_by_sms(client, "13800001003")
    grant_roles([RoleCode.user.value, RoleCode.admin.value], admin_login["user_id"])

    admin_headers = {"Authorization": f"Bearer {admin_login['access_token']}"}
    list_response = client.get("/api/v1/roles", headers=admin_headers)

    assert list_response.status_code == 200
    role_codes = {role["code"] for role in list_response.json()["data"]}
    assert {role.value for role in RoleCode}.issubset(role_codes)

    update_response = client.patch(
        f"/api/v1/roles/users/{target_login['user_id']}",
        headers=admin_headers,
        json={"role_codes": [RoleCode.user.value, RoleCode.merchant.value]},
    )

    assert update_response.status_code == 200
    updated_codes = {role["code"] for role in update_response.json()["data"]["roles"]}
    assert updated_codes == {RoleCode.user.value, RoleCode.merchant.value}

    me_response = client.get(
        "/api/v1/roles/me",
        headers={"Authorization": f"Bearer {target_login['access_token']}"},
    )

    assert me_response.status_code == 200
    me_codes = {role["code"] for role in me_response.json()["data"]["roles"]}
    assert me_codes == {RoleCode.user.value, RoleCode.merchant.value}


def test_admin_assign_roles_rejects_unknown_code(client: TestClient):
    admin_login = login_by_sms(client, "13800001004")
    target_login = login_by_sms(client, "13800001005")
    grant_roles([RoleCode.user.value, RoleCode.admin.value], admin_login["user_id"])

    response = client.patch(
        f"/api/v1/roles/users/{target_login['user_id']}",
        headers={"Authorization": f"Bearer {admin_login['access_token']}"},
        json={"role_codes": [RoleCode.user.value, "ghost"]},
    )

    assert response.status_code == 404
    assert response.json()["code"] == "NOT_FOUND"
