import os

os.environ.setdefault("SKIP_RESTAURANT_BOOTSTRAP", "1")
import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as _orders_csv:
    _ORDERS_CSV_SESSION = _orders_csv.name
os.environ.setdefault("ORDERS_CSV_PATH", _ORDERS_CSV_SESSION)

from backend.app import auth_session
from backend.app.main import app


@pytest.fixture()
def test_context():
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as temp_users_csv:
        temp_users_csv_path = temp_users_csv.name
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as temp_restaurants_csv:
        temp_restaurants_csv_path = temp_restaurants_csv.name
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as temp_menu_items_csv:
        temp_menu_items_csv_path = temp_menu_items_csv.name

    previous_auth_users_csv_path = os.environ.get("AUTH_USERS_CSV_PATH")
    previous_restaurants_csv_path = os.environ.get("RESTAURANTS_CSV_PATH")
    previous_menu_items_csv_path = os.environ.get("MENU_ITEMS_CSV_PATH")
    os.environ["AUTH_USERS_CSV_PATH"] = temp_users_csv_path
    os.environ["RESTAURANTS_CSV_PATH"] = temp_restaurants_csv_path
    os.environ["MENU_ITEMS_CSV_PATH"] = temp_menu_items_csv_path

    try:
        with TestClient(app) as client:
            yield {
                "client": client,
                "auth_users_csv_path": Path(temp_users_csv_path),
                "restaurants_csv_path": Path(temp_restaurants_csv_path),
                "menu_items_csv_path": Path(temp_menu_items_csv_path),
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
        if previous_menu_items_csv_path is None:
            os.environ.pop("MENU_ITEMS_CSV_PATH", None)
        else:
            os.environ["MENU_ITEMS_CSV_PATH"] = previous_menu_items_csv_path
        auth_session.clear_sessions()
        os.remove(temp_users_csv_path)
        os.remove(temp_restaurants_csv_path)
        os.remove(temp_menu_items_csv_path)
