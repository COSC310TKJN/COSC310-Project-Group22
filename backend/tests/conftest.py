import os
import pytest
from backend.repositories.order_repo import orders_db


@pytest.fixture(autouse=True)
def clear_data(tmp_path, monkeypatch):
    orders_csv_path = tmp_path / "orders.csv"
    monkeypatch.setenv("ORDERS_CSV_PATH", str(orders_csv_path))
    orders_db.clear()
    yield
    orders_db.clear()