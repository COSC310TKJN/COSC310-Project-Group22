from backend.app.menu_storage import load_menu_items
from backend.app.restaurant_storage import load_restaurants


def login_user(client, username, password) -> int:
    response = client.post(
        "/auth/login",
        json={"username": username, "password": password},
    )
    assert response.status_code == 200
    return response.json()["id"]


def register_user(client, username, password, role) -> int:
    response = client.post(
        "/auth/register",
        json={"username": username, "password": password, "role": role},
    )
    assert response.status_code == 201
    return response.json()["id"]


def test_unauthenticated_restaurant_create_is_rejected(test_context):
    client = test_context["client"]

    response = client.post(
        "/restaurants",
        json={"name": "Denied Diner", "cuisine_type": "American", "address": "Nowhere"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Authentication required."


def test_regular_user_cannot_create_restaurant(test_context):
    client = test_context["client"]

    register_user(client, "regular_restaurant_user", "UserPass123", "user")
    user_id = login_user(client, "regular_restaurant_user", "UserPass123")

    response = client.post(
        "/restaurants",
        json={"name": "Denied Diner", "cuisine_type": "American", "address": "Nowhere"},
        headers={"X-User-Id": str(user_id)},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Manager role required."
    assert all(restaurant.name != "Denied Diner" for restaurant in load_restaurants())


def test_manager_can_create_restaurant(test_context):
    client = test_context["client"]

    register_user(client, "manager_restaurant_user", "ManagerPass123", "manager")
    manager_id = login_user(client, "manager_restaurant_user", "ManagerPass123")

    response = client.post(
        "/restaurants",
        json={"name": "Manager Bistro", "cuisine_type": "Italian", "address": "Main Street"},
        headers={"X-User-Id": str(manager_id)},
    )

    assert response.status_code == 201
    assert response.json()["name"] == "Manager Bistro"
    assert any(restaurant.name == "Manager Bistro" for restaurant in load_restaurants())


def test_regular_user_cannot_create_menu_item(test_context):
    client = test_context["client"]

    register_user(client, "regular_menu_user", "UserPass123", "user")
    user_id = login_user(client, "regular_menu_user", "UserPass123")

    response = client.post(
        "/menu-items",
        json={
            "restaurant_id": 1,
            "name": "Updated Soup",
            "base_price": 6.0,
            "estimated_price": 6.0,
            "description": "Hot soup",
            "category": "Starter",
        },
        headers={"X-User-Id": str(user_id)},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Manager role required."
    assert all(menu_item.name != "Updated Soup" for menu_item in load_menu_items())


def test_manager_can_create_menu_item(test_context):
    client = test_context["client"]

    register_user(client, "manager_menu_user", "ManagerPass123", "manager")
    manager_id = login_user(client, "manager_menu_user", "ManagerPass123")

    response = client.post(
        "/menu-items",
        json={
            "restaurant_id": 1,
            "name": "Noodles",
            "base_price": 8.0,
            "estimated_price": 8.0,
        },
        headers={"X-User-Id": str(manager_id)},
    )

    assert response.status_code == 201
    assert any(menu_item.name == "Noodles" for menu_item in load_menu_items())
