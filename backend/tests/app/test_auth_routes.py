import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.app.routes import auth_routes
from backend.app.security import hash_password
from backend.models.user import User
from backend.schemas.user_schema import UserRegisterRequest


def test_get_current_user_returns_user(test_context):
    session_local = test_context["SessionLocal"]
    db: Session = session_local()

    try:
        user = User(
            username="current_user",
            hashed_password=hash_password("Password123"),
            role="user",
            is_manager=False,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        current_user = auth_routes.get_current_user(x_user_id=user.id, db=db)

        assert current_user.id == user.id
        assert current_user.username == "current_user"
    finally:
        db.close()


def test_get_current_user_rejects_missing_header(test_context):
    session_local = test_context["SessionLocal"]
    db: Session = session_local()

    try:
        with pytest.raises(HTTPException) as error:
            auth_routes.get_current_user(x_user_id=None, db=db)

        assert error.value.status_code == 401
        assert error.value.detail == "Authentication required."
    finally:
        db.close()


def test_get_current_user_rejects_unknown_user(test_context):
    session_local = test_context["SessionLocal"]
    db: Session = session_local()

    try:
        with pytest.raises(HTTPException) as error:
            auth_routes.get_current_user(x_user_id=999, db=db)

        assert error.value.status_code == 401
        assert error.value.detail == "Invalid user credentials."
    finally:
        db.close()


def test_require_manager_returns_manager():
    manager = User(
        id=1,
        username="manager_user",
        hashed_password="hashed",
        role="manager",
        is_manager=True,
    )

    returned_user = auth_routes.require_manager(manager)

    assert returned_user is manager


def test_require_manager_rejects_regular_user():
    user = User(
        id=1,
        username="regular_user",
        hashed_password="hashed",
        role="user",
        is_manager=False,
    )

    with pytest.raises(HTTPException) as error:
        auth_routes.require_manager(user)

    assert error.value.status_code == 403
    assert error.value.detail == "Manager role required."


def test_register_user_creates_regular_user(test_context):
    session_local = test_context["SessionLocal"]
    db: Session = session_local()

    try:
        payload = UserRegisterRequest(username="new_user", password="StrongPass123", role="user")

        response = auth_routes.register_user(payload, db)

        assert response.username == "new_user"
        assert response.role == "user"
        assert response.is_manager is False

        stored_user = db.query(User).filter(User.username == "new_user").first()
        assert stored_user is not None
        assert stored_user.hashed_password == hash_password("StrongPass123")
    finally:
        db.close()


def test_register_user_rejects_duplicate_username(test_context):
    session_local = test_context["SessionLocal"]
    db: Session = session_local()

    try:
        existing_user = User(
            username="duplicate_user",
            hashed_password=hash_password("StrongPass123"),
            role="user",
            is_manager=False,
        )
        db.add(existing_user)
        db.commit()

        payload = UserRegisterRequest(
            username="duplicate_user",
            password="AnotherPass123",
            role="user",
        )

        with pytest.raises(HTTPException) as error:
            auth_routes.register_user(payload, db)

        assert error.value.status_code == 409
        assert error.value.detail == "Username already exists."
    finally:
        db.close()


def test_register_user_creates_manager(test_context):
    session_local = test_context["SessionLocal"]
    db: Session = session_local()

    try:
        payload = UserRegisterRequest(username="manager_one", password="ManagerPass123", role="manager")

        response = auth_routes.register_user(payload, db)

        assert response.role == "manager"
        assert response.is_manager is True
    finally:
        db.close()


def test_user_portal_returns_message():
    user = User(
        id=1,
        username="portal_user",
        hashed_password="hashed",
        role="user",
        is_manager=False,
    )

    response = auth_routes.user_portal(user)

    assert response == {"message": "Welcome portal_user. User portal access granted."}


def test_manager_portal_returns_message():
    manager = User(
        id=1,
        username="portal_manager",
        hashed_password="hashed",
        role="manager",
        is_manager=True,
    )

    response = auth_routes.manager_portal(manager)

    assert response == {"message": "Welcome portal_manager. Manager portal access granted."}
