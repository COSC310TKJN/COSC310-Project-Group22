import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.database import Base, get_db
from backend.app.main import app

TEST_DATABASE_URL = "sqlite:///./test_reviews.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def test_rating_range_1_to_5():
  order_id = _create_delivered_order()
  r = client.post("/reviews/", json={"order_id": order_id, "rating": 0})
  assert r.status_code == 422
  r = client.post("/reviews/", json={"order_id": order_id, "rating": 6})
  assert r.status_code == 422
