from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.models.restaurant import Restaurant


def test_list_restaurants_returns_persisted_restaurants(test_context):
    client: TestClient = test_context["client"]
    session_local = test_context["SessionLocal"]

    db: Session = session_local()
    try:
        db.add_all(
            [
                Restaurant(id=2, name="Restaurant 2", cuisine_type="Asian", address="City_2"),
                Restaurant(id=1, name="Restaurant 1", cuisine_type="American", address="City_1"),
            ]
        )
        db.commit()

        response = client.get("/restaurants/")

        assert response.status_code == 200
        assert response.json() == [
            {"id": 1, "name": "Restaurant 1", "cuisine_type": "American", "address": "City_1"},
            {"id": 2, "name": "Restaurant 2", "cuisine_type": "Asian", "address": "City_2"},
        ]
    finally:
        db.close()
