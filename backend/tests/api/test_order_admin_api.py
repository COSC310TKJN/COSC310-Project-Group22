import pytest
from fastapi.testclient import TestClient

from backend.app import auth_session
from backend.app.main import app
from backend.app.roles import Role
from backend.app.security import hash_password
from backend.app.user_storage import append_user, next_user_id
from backend.models.user import User
from backend.repositories.order_repo import orders_db

client = TestClient(app)


def _order_json(oid: str = "adm-1"):
    return {
        "order_id": oid,
        "restaurant_id": 10,
        "food_item": "Pizza",
        "order_time": "2025-03-11T12:00:00",
        "order_value": 20,
        "delivery_method": "bike",
        "delivery_distance": 5,
        "customer_id": "C1",
    }


@pytest.fixture(autouse=True)
def isolated_storage(tmp_path, monkeypatch):
    monkeypatch.setenv("AUTH_USERS_CSV_PATH", str(tmp_path / "users.csv"))
    monkeypatch.setenv("ORDERS_CSV_PATH", str(tmp_path / "orders.csv"))
    orders_db.clear()
    auth_session.clear_sessions()
    yield
    orders_db.clear()
    auth_session.clear_sessions()


def _append_manager(username: str = "mgr_adm") -> int:
    uid = next_user_id()
    append_user(
        User(
            id=uid,
            username=username,
            hashed_password=hash_password("pw12345"),
            role=Role.MANAGER,
            is_manager=True,
        )
    )
    r = client.post("/auth/login", json={"username": username, "password": "pw12345"})
    assert r.status_code == 200
    return uid


def _append_regular(username: str = "usr_adm") -> int:
    uid = next_user_id()
    append_user(
        User(
            id=uid,
            username=username,
            hashed_password=hash_password("pw12345"),
            role=Role.USER,
            is_manager=False,
        )
    )
    r = client.post("/auth/login", json={"username": username, "password": "pw12345"})
    assert r.status_code == 200
    return uid


def test_admin_list_orders_requires_manager():
    _append_manager()
    client.post("/orders", json=_order_json())
    no_header = client.get("/orders/admin")
    assert no_header.status_code == 401

    uid = _append_regular("u_block_list")
    blocked = client.get("/orders/admin", headers={"X-User-Id": str(uid)})
    assert blocked.status_code == 403


def test_admin_list_orders_success():
    _append_manager("mgr_list")
    client.post("/orders", json=_order_json("a"))
    client.post("/orders", json=_order_json("b"))
    mid = _append_manager("mgr_list2")
    r = client.get("/orders/admin", headers={"X-User-Id": str(mid)})
    assert r.status_code == 200
    assert len(r.json()["orders"]) == 2


def test_admin_patch_order_requires_manager():
    client.post("/orders", json=_order_json())
    r = client.patch(
        "/orders/admin/adm-1",
        json={"food_item": "Sushi", "order_value": 30},
    )
    assert r.status_code == 401

    uid = _append_regular("u_block_patch")
    r2 = client.patch(
        "/orders/admin/adm-1",
        json={"food_item": "Sushi", "order_value": 30},
        headers={"X-User-Id": str(uid)},
    )
    assert r2.status_code == 403


def test_admin_patch_order_success():
    _append_manager("mgr_patch")
    client.post("/orders", json=_order_json())
    mid = _append_manager("mgr_patch2")
    r = client.patch(
        "/orders/admin/adm-1",
        json={
            "food_item": "2× Burger",
            "order_value": 35.5,
            "delivery_method": "car",
            "coupon_code": "",
        },
        headers={"X-User-Id": str(mid)},
    )
    assert r.status_code == 200
    data = r.json()["order"]
    assert data["food_item"] == "2× Burger"
    assert data["order_value"] == 35.5
    assert data["delivery_method"] == "car"
    assert data.get("coupon_code") in (None, "")


def test_admin_patch_rejects_unknown_field():
    _append_manager("mgr_bad")
    client.post("/orders", json=_order_json())
    mid = _append_manager("mgr_bad2")
    r = client.patch(
        "/orders/admin/adm-1",
        json={"food_item": "X", "order_value": 1, "customer_id": "hacker"},
        headers={"X-User-Id": str(mid)},
    )
    assert r.status_code == 422
