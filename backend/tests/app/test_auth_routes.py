import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.app.routes import auth_routes
from backend.app.security import hash_password
from backend.models.user import User
from backend.schemas.user_schema import UserRegisterRequest




def test_register_user_creates_regular_user(test_context):
    session_local = test_context["SessionLocal"]
    db: Session = session_local()

    try:
        payload = UserRegisterRequest(username="new_user", password="StrongPass123")

        response = auth_routes.register_user(payload, db)

        assert response.username == "new_user"

        stored_user = db.query(User).filter(User.username == "new_user").first()
        assert stored_user is not None
    finally:
        db.close()


def test_register_user_rejects_duplicate_username(test_context):
    session_local = test_context["SessionLocal"]
    db: Session = session_local()

    try:
        existing_user = User(
            username="duplicate_user",
            hashed_password=hash_password("StrongPass123"),
            
        )
        db.add(existing_user)
        db.commit()

        payload = UserRegisterRequest(
            username="duplicate_user",
            password="AnotherPass123",
            
        )

        with pytest.raises(HTTPException) as error:
            auth_routes.register_user(payload, db)

        assert error.value.status_code == 409
        assert error.value.detail == "Username already exists."
    finally:
        db.close()