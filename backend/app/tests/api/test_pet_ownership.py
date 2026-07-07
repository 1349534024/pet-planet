from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.deps import get_db
from app.db.base import Base
from app.main import app
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


def login_headers(client: TestClient, phone: str) -> dict[str, str]:
    response = client.post("/api/v1/auth/login/sms", json={"phone": phone, "code": "123456"})
    assert response.status_code == 200
    token = response.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


def create_pet(client: TestClient, headers: dict[str, str], name: str) -> dict:
    response = client.post(
        "/api/v1/pets",
        headers=headers,
        json={"name": name, "type": "cat", "gender": "unknown"},
    )
    assert response.status_code == 200
    return response.json()["data"]


def test_pet_list_only_returns_current_users_pets(client: TestClient):
    owner_headers = login_headers(client, "13800003000")
    other_headers = login_headers(client, "13800003001")
    create_pet(client, owner_headers, "年糕")
    create_pet(client, other_headers, "小鱼")

    response = client.get("/api/v1/pets", headers=owner_headers)

    assert response.status_code == 200
    items = response.json()["data"]["items"]
    assert [item["name"] for item in items] == ["年糕"]


def test_user_cannot_read_update_or_delete_other_users_pet(client: TestClient):
    owner_headers = login_headers(client, "13800003002")
    other_headers = login_headers(client, "13800003003")
    pet = create_pet(client, owner_headers, "布丁")

    get_response = client.get(f"/api/v1/pets/{pet['id']}", headers=other_headers)
    update_response = client.patch(
        f"/api/v1/pets/{pet['id']}",
        headers=other_headers,
        json={"name": "偷改名"},
    )
    delete_response = client.delete(f"/api/v1/pets/{pet['id']}", headers=other_headers)

    assert get_response.status_code == 403
    assert get_response.json()["code"] == "PET_PERMISSION_DENIED"
    assert update_response.status_code == 403
    assert update_response.json()["code"] == "PET_PERMISSION_DENIED"
    assert delete_response.status_code == 403
    assert delete_response.json()["code"] == "PET_PERMISSION_DENIED"


def test_owner_can_update_and_soft_delete_pet(client: TestClient):
    owner_headers = login_headers(client, "13800003004")
    pet = create_pet(client, owner_headers, "豆包")

    update_response = client.patch(
        f"/api/v1/pets/{pet['id']}",
        headers=owner_headers,
        json={"name": "豆包包", "weight": "4.2kg"},
    )
    delete_response = client.delete(f"/api/v1/pets/{pet['id']}", headers=owner_headers)
    get_deleted_response = client.get(f"/api/v1/pets/{pet['id']}", headers=owner_headers)
    list_response = client.get("/api/v1/pets", headers=owner_headers)

    assert update_response.status_code == 200
    assert update_response.json()["data"]["name"] == "豆包包"
    assert delete_response.status_code == 200
    assert get_deleted_response.status_code == 404
    assert list_response.json()["data"]["items"] == []


def test_growth_records_are_limited_to_pet_owner(client: TestClient):
    owner_headers = login_headers(client, "13800003005")
    other_headers = login_headers(client, "13800003006")
    pet = create_pet(client, owner_headers, "汤圆")

    create_response = client.post(
        f"/api/v1/pets/{pet['id']}/records",
        headers=owner_headers,
        json={"record_type": "daily", "title": "第一次洗澡", "content": "很乖"},
    )
    assert create_response.status_code == 200
    record = create_response.json()["data"]

    other_list_response = client.get(f"/api/v1/pets/{pet['id']}/records", headers=other_headers)
    other_get_response = client.get(f"/api/v1/pets/{pet['id']}/records/{record['id']}", headers=other_headers)
    owner_update_response = client.patch(
        f"/api/v1/pets/{pet['id']}/records/{record['id']}",
        headers=owner_headers,
        json={"title": "第一次洗澡成功"},
    )
    owner_delete_response = client.delete(f"/api/v1/pets/{pet['id']}/records/{record['id']}", headers=owner_headers)
    owner_list_after_delete = client.get(f"/api/v1/pets/{pet['id']}/records", headers=owner_headers)

    assert other_list_response.status_code == 403
    assert other_list_response.json()["code"] == "PET_PERMISSION_DENIED"
    assert other_get_response.status_code == 403
    assert other_get_response.json()["code"] == "PET_PERMISSION_DENIED"
    assert owner_update_response.status_code == 200
    assert owner_update_response.json()["data"]["title"] == "第一次洗澡成功"
    assert owner_delete_response.status_code == 200
    assert owner_list_after_delete.json()["data"] == []


def test_reminder_rejects_other_users_pet(client: TestClient):
    owner_headers = login_headers(client, "13800003007")
    other_headers = login_headers(client, "13800003008")
    pet = create_pet(client, owner_headers, "芝麻")

    response = client.post(
        "/api/v1/reminders",
        headers=other_headers,
        json={
            "pet_id": pet["id"],
            "reminder_type": "vaccine",
            "title": "疫苗提醒",
            "remind_at": "2026-08-01T09:00:00Z",
        },
    )

    assert response.status_code == 403
    assert response.json()["code"] == "PET_PERMISSION_DENIED"
