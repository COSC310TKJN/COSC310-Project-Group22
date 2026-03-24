from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.models.user import User


def test_register_user_success_persists_user_record(test_context):
    client: TestClient = test_context["client"]
    session_local = test_context["SessionLocal"]

    response = client.post(
        "/auth/register",
        json={"username": "alice_123", "password": "StrongPass123"},
    )

    assert response.status_code == 201
    response_body = response.json()
    assert response_body["username"] == "alice_123"
    assert response_body["is_manager"] is False
    assert response_body["role"] == "user"
    assert response_body["message"] == "User registered successfully."

    db: Session = session_local()
    try:
        stored_user = db.query(User).filter(User.username == "alice_123").first()
        assert stored_user is not None
        assert stored_user.role == "user"
        assert stored_user.hashed_password != "StrongPass123"
    finally:
        db.close()


def test_register_user_duplicate_username_rejected(test_context):
    client: TestClient = test_context["client"]

    first_response = client.post(
        "/auth/register",
        json={"username": "duplicate_user", "password": "StrongPass123"},
    )
    assert first_response.status_code == 201

    second_response = client.post(
        "/auth/register",
        json={"username": "duplicate_user", "password": "AnotherStrongPass456"},
    )

    assert second_response.status_code == 409
    assert second_response.json()["detail"] == "Username already exists."


def test_register_user_manager_role_is_assigned_and_stored(test_context):
    client: TestClient = test_context["client"]
    session_local = test_context["SessionLocal"]

    response = client.post(
        "/auth/register",
        json={"username": "owner_1", "password": "ManagerPass123", "role": "manager"},
    )

    assert response.status_code == 201
    response_body = response.json()
    assert response_body["role"] == "manager"
    assert response_body["is_manager"] is True

    db: Session = session_local()
    try:
        stored_user = db.query(User).filter(User.username == "owner_1").first()
        assert stored_user is not None
        assert stored_user.role == "manager"
        assert stored_user.is_manager is True
    finally:
        db.close()


def test_role_based_endpoint_access_control(test_context):
    client: TestClient = test_context["client"]

    user_response = client.post(
        "/auth/register",
        json={"username": "regular_user", "password": "RegularPass123", "role": "user"},
    )
    assert user_response.status_code == 201
    user_id = user_response.json()["id"]

    manager_response = client.post(
        "/auth/register",
        json={"username": "restaurant_owner", "password": "OwnerPass123", "role": "manager"},
    )
    assert manager_response.status_code == 201
    manager_id = manager_response.json()["id"]

    user_portal_response = client.get("/portal/user", headers={"X-User-Id": str(user_id)})
    assert user_portal_response.status_code == 200

    blocked_manager_response = client.get("/portal/manager", headers={"X-User-Id": str(user_id)})
    assert blocked_manager_response.status_code == 403
    assert blocked_manager_response.json()["detail"] == "Manager role required."

    manager_portal_response = client.get("/portal/manager", headers={"X-User-Id": str(manager_id)})
    assert manager_portal_response.status_code == 200
