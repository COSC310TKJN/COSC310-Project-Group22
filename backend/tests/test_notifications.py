def test_multiple_status_changes():
    client.post("/notifications/status-change?user_id=user_6&order_id=600&new_status=preparing")
    client.post("/notifications/status-change?user_id=user_6&order_id=600&new_status=out_for_delivery")
    response = client.get("/notifications/?user_id=user_6")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    messages = [n["message"] for n in data]
    assert any("preparing" in m for m in messages)
    assert any("out_for_delivery" in m for m in messages)


def test_delivery_notification():
    response = client.post("/notifications/delivery?user_id=user_7&order_id=700")
    assert response.status_code == 201
    data = response.json()
    assert data["user_id"] == "user_7"
    assert data["notification_type"] == "delivery"
    assert data["order_id"] == 700
    assert "delivered" in data["message"].lower()


def test_manager_notified_new_order():
    response = client.post("/notifications/manager/new-order?manager_id=manager_1&order_id=800")
    assert response.status_code == 201
    data = response.json()
    assert data["user_id"] == "manager_1"
    assert data["notification_type"] == "manager_new_order"
    assert data["order_id"] == 800
    assert "order #800" in data["message"]
    notifs = client.get("/notifications/?user_id=manager_1")
    assert len(notifs.json()) == 1