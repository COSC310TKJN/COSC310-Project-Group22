import pytest
from fastapi import HTTPException

from backend.app import auth_session
from backend.app.roles import Role
from backend.app.routes import auth_routes
from backend.app.security import hash_password
from backend.app.user_storage import append_user, find_user_by_username, next_user_id
from backend.models.user import User
from backend.schemas.user_schema import UserLoginRequest, UserRegisterRequest


def seed_user(username: str, password: str, role: str = Role.USER) -> User:
    user = User(
        id=next_user_id(),
        username=username,
        hashed_password=hash_password(password),
        role=role,
        is_manager=role == Role.MANAGER,
    )
    append_user(user)
    return user


def test_get_current_user_returns_user(test_context):
    user = seed_user("current_user", "Password123")
    auth_session.login_session(user.id)

    current_user = auth_routes.get_current_user(x_user_id=user.id)

    assert current_user.id == user.id
    assert current_user.username == "current_user"


def test_get_current_user_rejects_missing_header():
    with pytest.raises(HTTPException) as error:
        auth_routes.get_current_user(x_user_id=None)

    assert error.value.status_code == 401
    assert error.value.detail == "Authentication required."


def test_get_current_user_rejects_unknown_user():
    with pytest.raises(HTTPException) as error:
        auth_routes.get_current_user(x_user_id=999)

    assert error.value.status_code == 401
    assert error.value.detail == "Invalid user credentials."


def test_require_manager_returns_manager():
    manager = User(
        id=1,
        username="manager_user",
        hashed_password="hashed",
        role=Role.MANAGER,
        is_manager=True,
    )

    returned_user = auth_routes.require_manager(manager)

    assert returned_user is manager


def test_require_manager_rejects_regular_user():
    user = User(
        id=1,
        username="regular_user",
        hashed_password="hashed",
        role=Role.USER,
        is_manager=False,
    )

    with pytest.raises(HTTPException) as error:
        auth_routes.require_manager(user)

    assert error.value.status_code == 403
    assert error.value.detail == "Manager role required."


def test_register_user_creates_regular_user(test_context):
    payload = UserRegisterRequest(username="new_user", password="StrongPass123", role=Role.USER)

    response = auth_routes.register_user(payload)

    assert response.username == "new_user"
    assert response.role == Role.USER
    assert response.is_manager is False

    stored_user = find_user_by_username("new_user")
    assert stored_user is not None
    assert stored_user.hashed_password == hash_password("StrongPass123")


def test_register_user_rejects_duplicate_username(test_context):
    seed_user("duplicate_user", "StrongPass123")

    payload = UserRegisterRequest(
        username="duplicate_user",
        password="AnotherPass123",
        role=Role.USER,
    )

    with pytest.raises(HTTPException) as error:
        auth_routes.register_user(payload)

    assert error.value.status_code == 409
    assert error.value.detail == "Username already exists."


def test_register_user_creates_manager(test_context):
    payload = UserRegisterRequest(username="manager_one", password="ManagerPass123", role=Role.MANAGER)

    response = auth_routes.register_user(payload)

    assert response.role == Role.MANAGER
    assert response.is_manager is True


def test_login_user_returns_existing_user(test_context):
    user = seed_user("login_user", "StrongPass123")

    payload = UserLoginRequest(username="login_user", password="StrongPass123")
    response = auth_routes.login_user(payload)

    assert response.id == user.id
    assert response.username == "login_user"
    assert response.role == Role.USER
    assert response.is_manager is False
    assert auth_session.is_logged_in(user.id) is True


def test_login_user_rejects_invalid_credentials(test_context):
    seed_user("login_user", "StrongPass123")

    payload = UserLoginRequest(username="login_user", password="WrongPass123")

    with pytest.raises(HTTPException) as error:
        auth_routes.login_user(payload)

    assert error.value.status_code == 401
    assert error.value.detail == "Invalid username or password."


def test_logout_user_removes_logged_in_user(test_context):
    user = seed_user("logout_user", "StrongPass123")
    auth_session.login_session(user.id)

    response = auth_routes.logout_user(user)

    assert response == {"message": "Logout successful."}
    assert auth_session.is_logged_in(user.id) is False


def test_user_portal_returns_message():
    user = User(
        id=1,
        username="portal_user",
        hashed_password="hashed",
        role=Role.USER,
        is_manager=False,
    )

    response = auth_routes.user_portal(user)

    assert response == {"message": "Welcome portal_user. User portal access granted."}


def test_manager_portal_returns_message():
    manager = User(
        id=1,
        username="portal_manager",
        hashed_password="hashed",
        role=Role.MANAGER,
        is_manager=True,
    )

    response = auth_routes.manager_portal(manager)

    assert response == {"message": "Welcome portal_manager. Manager portal access granted."}
