import os

os.environ.setdefault("SKIP_RESTAURANT_BOOTSTRAP", "1")
import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.database import Base, get_db
from backend.app.main import app
from backend.app.routes import auth_routes


@pytest.fixture()
def test_context():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as temp_db:
        temp_db_path = temp_db.name
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as temp_users_csv:
        temp_users_csv_path = temp_users_csv.name
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as temp_restaurants_csv:
        temp_restaurants_csv_path = temp_restaurants_csv.name

    test_engine = create_engine(
        f"sqlite:///{temp_db_path}",
        connect_args={"check_same_thread": False},
    )
    test_session_local = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

    Base.metadata.create_all(bind=test_engine)

    def override_get_db():
        db = test_session_local()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    previous_auth_users_csv_path = os.environ.get("AUTH_USERS_CSV_PATH")
    previous_restaurants_csv_path = os.environ.get("RESTAURANTS_CSV_PATH")
    os.environ["AUTH_USERS_CSV_PATH"] = temp_users_csv_path
    os.environ["RESTAURANTS_CSV_PATH"] = temp_restaurants_csv_path

    try:
        with TestClient(app) as client:
            yield {
                "client": client,
                "SessionLocal": test_session_local,
                "auth_users_csv_path": Path(temp_users_csv_path),
                "restaurants_csv_path": Path(temp_restaurants_csv_path),
            }
    finally:
        if previous_auth_users_csv_path is None:
            os.environ.pop("AUTH_USERS_CSV_PATH", None)
        else:
            os.environ["AUTH_USERS_CSV_PATH"] = previous_auth_users_csv_path
        if previous_restaurants_csv_path is None:
            os.environ.pop("RESTAURANTS_CSV_PATH", None)
        else:
            os.environ["RESTAURANTS_CSV_PATH"] = previous_restaurants_csv_path
        app.dependency_overrides.clear()
        auth_routes.logged_in_users.clear()
        Base.metadata.drop_all(bind=test_engine)
        test_engine.dispose()
        os.remove(temp_db_path)
        os.remove(temp_users_csv_path)
        os.remove(temp_restaurants_csv_path)
