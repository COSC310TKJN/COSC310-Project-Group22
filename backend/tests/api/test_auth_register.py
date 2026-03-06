"""Tests for FR1 user registration behavior."""

import os
import tempfile

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from backend.app.database import Base, get_db
from backend.app.main import app
from backend.models.user import User


# Build a per-test client backed by an isolated temporary SQLite database.
@pytest.fixture()
def test_context():
    # Create a temporary database file for this test case.
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as temp_db:
        temp_db_path = temp_db.name

    # Configure SQLAlchemy engine/session for the temporary database.
    test_engine = create_engine(
        f"sqlite:///{temp_db_path}",
        connect_args={"check_same_thread": False},
    )
    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

    # Create required tables in the temporary database.
    Base.metadata.create_all(bind=test_engine)

    # Override the application DB dependency to use test sessions.
    def override_get_db():
        # Open a fresh session for each request.
        db = TestSessionLocal()
        try:
            # Provide session to the route handler.
            yield db
        finally:
            # Always close the session after request handling.
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    try:
        # Yield a test client and session factory so tests can inspect persisted rows.
        with TestClient(app) as client:
            yield {"client": client, "SessionLocal": TestSessionLocal}
    finally:
        # Reset overrides and clean up DB artifacts after each test.
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=test_engine)
        os.remove(temp_db_path)


# FR1: user can register with a unique username and password.
def test_register_user_success_persists_user_record(test_context):
    # Grab the FastAPI test client and DB session maker from the fixture.
    client: TestClient = test_context["client"]
    SessionLocal = test_context["SessionLocal"]

    # Send a valid registration request.
    response = client.post(
        "/auth/register",
        json={"username": "alice_123", "password": "StrongPass123"},
    )

    # Confirm API returns created status for successful registration.
    assert response.status_code == 201
    response_body = response.json()
    assert response_body["username"] == "alice_123"
    assert response_body["is_manager"] is False
    assert response_body["role"] == "user"
    assert response_body["message"] == "User registered successfully."

    # Confirm the user row exists in the database and password is hashed.
    db: Session = SessionLocal()
    try:
        stored_user = db.query(User).filter(User.username == "alice_123").first()
        assert stored_user is not None
        assert stored_user.role == "user"
        assert stored_user.hashed_password != "StrongPass123"
    finally:
        db.close()


# FR1: duplicate usernames are rejected by the registration endpoint.
def test_register_user_duplicate_username_rejected(test_context):
    # Grab the client from the fixture.
    client: TestClient = test_context["client"]

    # Create the first account with a unique username.
    first_response = client.post(
        "/auth/register",
        json={"username": "duplicate_user", "password": "StrongPass123"},
    )
    assert first_response.status_code == 201

    # Attempt to create a second account with the same username.
    second_response = client.post(
        "/auth/register",
        json={"username": "duplicate_user", "password": "AnotherStrongPass456"},
    )

    # Confirm API rejects duplicate usernames with 409 conflict.
    assert second_response.status_code == 409
    assert second_response.json()["detail"] == "Username already exists."


# FR2: account role is assigned at registration and persisted in user records.
def test_register_user_manager_role_is_assigned_and_stored(test_context):
    # Grab the test client and DB session maker from the fixture.
    client: TestClient = test_context["client"]
    SessionLocal = test_context["SessionLocal"]

    # Register a manager account by explicitly sending role="manager".
    response = client.post(
        "/auth/register",
        json={"username": "owner_1", "password": "ManagerPass123", "role": "manager"},
    )

    # Confirm manager role is reflected in the API response.
    assert response.status_code == 201
    response_body = response.json()
    assert response_body["role"] == "manager"
    assert response_body["is_manager"] is True

    # Confirm manager role is persisted in the database.
    db: Session = SessionLocal()
    try:
        stored_user = db.query(User).filter(User.username == "owner_1").first()
        assert stored_user is not None
        assert stored_user.role == "manager"
        assert stored_user.is_manager is True
    finally:
        db.close()


# FR2: regular users are denied manager-only endpoints while managers are allowed.
def test_role_based_endpoint_access_control(test_context):
    # Grab the test client from the fixture.
    client: TestClient = test_context["client"]

    # Register one regular user account.
    user_response = client.post(
        "/auth/register",
        json={"username": "regular_user", "password": "RegularPass123", "role": "user"},
    )
    assert user_response.status_code == 201
    user_id = user_response.json()["id"]

    # Register one manager account.
    manager_response = client.post(
        "/auth/register",
        json={"username": "restaurant_owner", "password": "OwnerPass123", "role": "manager"},
    )
    assert manager_response.status_code == 201
    manager_id = manager_response.json()["id"]

    # Confirm regular users can access general user endpoints.
    user_portal_response = client.get("/portal/user", headers={"X-User-Id": str(user_id)})
    assert user_portal_response.status_code == 200

    # Confirm regular users are blocked from manager-only endpoints.
    blocked_manager_response = client.get("/portal/manager", headers={"X-User-Id": str(user_id)})
    assert blocked_manager_response.status_code == 403
    assert blocked_manager_response.json()["detail"] == "Manager role required."

    # Confirm managers can access manager-only endpoints.
    manager_portal_response = client.get("/portal/manager", headers={"X-User-Id": str(manager_id)})
    assert manager_portal_response.status_code == 200
