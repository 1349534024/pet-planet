from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.deps import get_db
from app.db.base import Base
from app.main import app
from app.models.user import User
from app.models import file, operation_log, pet, user  # noqa: F401


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


def test_sms_login_me_update_password_login_flow(client: TestClient):
    login_response = client.post(
        "/api/v1/auth/login/sms",
        json={"phone": "13800000000", "code": "123456"},
    )

    assert login_response.status_code == 200
    login_data = login_response.json()["data"]
    access_token = login_data["access_token"]
    assert login_data["token_type"] == "bearer"
    assert login_data["roles"] == ["user"]

    headers = {"Authorization": f"Bearer {access_token}"}
    me_response = client.get("/api/v1/users/me", headers=headers)

    assert me_response.status_code == 200
    me_data = me_response.json()["data"]
    assert me_data["phone"] == "13800000000"
    assert me_data["status"] == "active"
    assert me_data["profile"]["has_pet"] is False

    update_response = client.patch(
        "/api/v1/users/me",
        headers=headers,
        json={"nickname": "星球居民", "city": "上海", "signature": "爱宠物", "has_pet": True},
    )

    assert update_response.status_code == 200
    update_data = update_response.json()["data"]
    assert update_data["nickname"] == "星球居民"
    assert update_data["profile"]["city"] == "上海"
    assert update_data["profile"]["has_pet"] is True

    set_password_response = client.post(
        "/api/v1/auth/password",
        headers=headers,
        json={"password": "pet123456"},
    )

    assert set_password_response.status_code == 200
    assert set_password_response.json()["data"] == {"password_set": True}

    password_login_response = client.post(
        "/api/v1/auth/login/password",
        json={"phone": "13800000000", "password": "pet123456"},
    )

    assert password_login_response.status_code == 200
    assert password_login_response.json()["data"]["user_id"] == login_data["user_id"]


def test_password_login_rejects_wrong_password(client: TestClient):
    login_response = client.post(
        "/api/v1/auth/login/sms",
        json={"phone": "13800000001", "code": "123456"},
    )
    access_token = login_response.json()["data"]["access_token"]

    client.post(
        "/api/v1/auth/password",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"password": "right123"},
    )
    response = client.post(
        "/api/v1/auth/login/password",
        json={"phone": "13800000001", "password": "wrong123"},
    )

    assert response.status_code == 400
    assert response.json()["code"] == "AUTH_INVALID_PASSWORD"


def test_sms_login_adds_default_role_for_existing_user(client: TestClient):
    override_get_db = app.dependency_overrides[get_db]
    db = next(override_get_db())
    try:
        db.add(User(phone="13800000003", nickname="旧用户"))
        db.commit()
    finally:
        db.close()

    response = client.post(
        "/api/v1/auth/login/sms",
        json={"phone": "13800000003", "code": "123456"},
    )

    assert response.status_code == 200
    assert response.json()["data"]["roles"] == ["user"]


def test_current_user_requires_access_token(client: TestClient):
    login_response = client.post(
        "/api/v1/auth/login/sms",
        json={"phone": "13800000002", "code": "123456"},
    )
    refresh_token = login_response.json()["data"]["refresh_token"]

    response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {refresh_token}"},
    )

    assert response.status_code == 401
    assert response.json()["code"] == "UNAUTHORIZED"


def test_logout_requires_login(client: TestClient):
    response = client.post("/api/v1/auth/logout")

    assert response.status_code == 401
    assert response.json()["code"] == "UNAUTHORIZED"
