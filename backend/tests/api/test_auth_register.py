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
    assert response_body["message"] == "User registered successfully."

    db: Session = session_local()
    try:
        stored_user = db.query(User).filter(User.username == "alice_123").first()
        assert stored_user is not None
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




