import csv

from fastapi.testclient import TestClient

from backend.app.roles import Role
from backend.app.user_storage import USER_HEADERS
from backend.app import csv_storage


def read_users_csv(csv_path):
    return csv_storage.read_rows(
        csv_path,
        USER_HEADERS,
    )


def login_user(client: TestClient, username: str, password: str) -> int:
    response = client.post(
        "/auth/login",
        json={"username": username, "password": password},
    )
    assert response.status_code == 200
    return response.json()["id"]


def test_register_user_success_persists_user_record(test_context):
    client: TestClient = test_context["client"]
    auth_users_csv_path = test_context["auth_users_csv_path"]

    response = client.post(
        "/auth/register",
        json={"username": "alice_123", "password": "StrongPass123"},
    )

    assert response.status_code == 201
    response_body = response.json()
    assert response_body["username"] == "alice_123"
    assert response_body["is_manager"] is False
    assert response_body["role"] == Role.USER
    assert response_body["message"] == "User registered successfully."

    stored_users = read_users_csv(auth_users_csv_path)
    assert len(stored_users) == 1
    assert stored_users[0]["username"] == "alice_123"
    assert stored_users[0]["role"] == Role.USER
    assert stored_users[0]["hashed_password"] != "StrongPass123"


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
    auth_users_csv_path = test_context["auth_users_csv_path"]

    response = client.post(
        "/auth/register",
        json={"username": "owner_1", "password": "ManagerPass123", "role": Role.MANAGER},
    )

    assert response.status_code == 201
    response_body = response.json()
    assert response_body["role"] == Role.MANAGER
    assert response_body["is_manager"] is True

    stored_users = read_users_csv(auth_users_csv_path)
    assert len(stored_users) == 1
    assert stored_users[0]["username"] == "owner_1"
    assert stored_users[0]["role"] == Role.MANAGER
    assert stored_users[0]["is_manager"] == "True"


def test_role_based_endpoint_access_control(test_context):
    client: TestClient = test_context["client"]

    user_response = client.post(
        "/auth/register",
        json={"username": "regular_user", "password": "RegularPass123", "role": Role.USER},
    )
    assert user_response.status_code == 201
    user_id = login_user(client, "regular_user", "RegularPass123")

    manager_response = client.post(
        "/auth/register",
        json={"username": "restaurant_owner", "password": "OwnerPass123", "role": Role.MANAGER},
    )
    assert manager_response.status_code == 201
    manager_id = login_user(client, "restaurant_owner", "OwnerPass123")

    user_portal_response = client.get("/portal/user", headers={"X-User-Id": str(user_id)})
    assert user_portal_response.status_code == 200

    blocked_manager_response = client.get("/portal/manager", headers={"X-User-Id": str(user_id)})
    assert blocked_manager_response.status_code == 403
    assert blocked_manager_response.json()["detail"] == "Manager role required."

    manager_portal_response = client.get("/portal/manager", headers={"X-User-Id": str(manager_id)})
    assert manager_portal_response.status_code == 200

    blocked_paid_orders_response = client.get(
        "/payments/manager/orders",
        headers={"X-User-Id": str(user_id)},
    )
    assert blocked_paid_orders_response.status_code == 403
    assert blocked_paid_orders_response.json()["detail"] == "Manager role required."

    manager_paid_orders_response = client.get(
        "/payments/manager/orders",
        headers={"X-User-Id": str(manager_id)},
    )
    assert manager_paid_orders_response.status_code == 200

    blocked_failed_payments_response = client.get(
        "/payments/manager/failed-payments",
        headers={"X-User-Id": str(user_id)},
    )
    assert blocked_failed_payments_response.status_code == 403
    assert blocked_failed_payments_response.json()["detail"] == "Manager role required."

    manager_failed_payments_response = client.get(
        "/payments/manager/failed-payments",
        headers={"X-User-Id": str(manager_id)},
    )
    assert manager_failed_payments_response.status_code == 200


def test_login_succeeds_with_valid_credentials(test_context):
    client: TestClient = test_context["client"]

    register_response = client.post(
        "/auth/register",
        json={"username": "login_user", "password": "StrongPass123"},
    )
    assert register_response.status_code == 201

    response = client.post(
        "/auth/login",
        json={"username": "login_user", "password": "StrongPass123"},
    )

    assert response.status_code == 200
    response_body = response.json()
    assert response_body["username"] == "login_user"
    assert response_body["role"] == Role.USER
    assert response_body["is_manager"] is False
    assert response_body["message"] == "Login successful."


def test_login_rejects_invalid_credentials(test_context):
    client: TestClient = test_context["client"]

    register_response = client.post(
        "/auth/register",
        json={"username": "login_user", "password": "StrongPass123"},
    )
    assert register_response.status_code == 201

    response = client.post(
        "/auth/login",
        json={"username": "login_user", "password": "WrongPass123"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid username or password."


def test_logout_blocks_future_protected_access(test_context):
    client: TestClient = test_context["client"]

    register_response = client.post(
        "/auth/register",
        json={"username": "logout_user", "password": "StrongPass123"},
    )
    assert register_response.status_code == 201
    user_id = login_user(client, "logout_user", "StrongPass123")

    logout_response = client.post("/auth/logout", headers={"X-User-Id": str(user_id)})
    assert logout_response.status_code == 200
    assert logout_response.json()["message"] == "Logout successful."

    blocked_response = client.get("/portal/user", headers={"X-User-Id": str(user_id)})
    assert blocked_response.status_code == 401
    assert blocked_response.json()["detail"] == "Login required."
