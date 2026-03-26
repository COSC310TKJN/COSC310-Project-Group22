import unittest
import pytest
import os
from pydantic import ValidationError
from backend.models.order import Order, OrderStatus
from backend.routes.order_routes import create_order
from backend.schemas.order_schema import OrderCreate
from backend.services.order_service import OrderService, orders_db


@pytest.fixture(autouse=True)
def clear_data(tmp_path, monkeypatch):
    orders_csv_path = tmp_path / "orders.csv"
    monkeypatch.setenv("ORDERS_CSV_PATH", str(orders_csv_path))
    orders_db.clear()
    yield
    orders_db.clear()
    

class TestOrders(unittest.TestCase):

    def test_create_order(self):

        order = Order(
            order_id="1",
            restaurant_id=10,
            food_item="Pizza",
            order_time="2025-03-11T12:00:00",
            order_value=20,
            delivery_method="bike",
            delivery_distance=5,
            customer_id="C1"
        )

        self.assertEqual(order.status, OrderStatus.CREATED)

    def test_negative_price(self):

        with self.assertRaises(ValueError):

            Order(
                order_id="2",
                restaurant_id=10,
                food_item="Burger",
                order_time="2025-03-11T12:00:00",
                order_value=-10,
                delivery_method="car",
                delivery_distance=4,
                customer_id="C2"
            )

    def test_no_modification(self):

        order = Order(
            order_id="3",
            restaurant_id=10,
            food_item="Pizza",
            order_time="2025-03-11T12:00:00",
            order_value=20,
            delivery_method="bike",
            delivery_distance=5,
            customer_id="C3"
        )

        orders_db[order.order_id] = order
        order.status = OrderStatus.COMPLETED

        with self.assertRaises(ValueError):
            OrderService.update_order(order.order_id, {"food_item": "Burger"})

    def test_order_to_database(self):

        order = OrderCreate(
            order_id="4",
            restaurant_id=10,
            food_item="Pasta",
            order_time="2025-03-11T12:00:00",
            order_value=18,
            delivery_method="car",
            delivery_distance=3,
            customer_id="C4"
        )

        created_order = OrderService.create_order(order)

        self.assertIn("4", orders_db)
        self.assertEqual(orders_db["4"], created_order)

    def test_cancel_order(self):

        order = OrderCreate(
            order_id="5",
            restaurant_id=10,
            food_item="Sushi",
            order_time="2025-03-11T12:00:00",
            order_value=30,
            delivery_method="bike",
            delivery_distance=6,
            customer_id="C5"
        )

        OrderService.create_order(order)
        cancelled_order = OrderService.cancel_order("5")

        self.assertEqual(cancelled_order.status, OrderStatus.CANCELLED)

    def test_invalid_order_value_type(self):

        with self.assertRaises(ValidationError):

            OrderCreate(
                order_id="6",
                restaurant_id=10,
                food_item="Burger",
                order_time="2025-03-11T12:00:00",
                order_value="twenty",
                delivery_method="car",
                delivery_distance=4,
                customer_id="C6"
            )

    def test_mixed_restaurant_rejected(self):

        with self.assertRaises(ValueError):

            OrderCreate(
                order_id="8",
                restaurant_id=[1, 2],
                food_item="Pizza, Burger",
                order_time="2025-03-11T12:00:00",
                order_value=30,
                delivery_method="bike",
                delivery_distance=5,
                customer_id="C8"
            )

    def test_single_restaurant_allowed(self):

        order = OrderCreate(
            order_id="9",
            restaurant_id=1,
            food_item="Pizza",
            order_time="2025-03-11T12:00:00",
            order_value=15,
            delivery_method="car",
            delivery_distance=3,
            customer_id="C9"
        )

        created_order = OrderService.create_order(order)

        self.assertEqual(created_order.restaurant_id, 1)

    def test_unauthenticated_user_pytest(self):

        order = OrderCreate(
            order_id="7",
            restaurant_id=10,
            food_item="Burger",
            order_time="2025-03-11T12:00:00",
            order_value=15,
            delivery_method="bike",
            delivery_distance=3,
            customer_id="INVALID"
        )

        with pytest.raises(ValueError):
            create_order(order)

    def test_authenticated_user_integration(self):

        order = OrderCreate(
            order_id="8",
            restaurant_id=10,
            food_item="Pizza",
            order_time="2025-03-11T12:00:00",
            order_value=20,
            delivery_method="car",
            delivery_distance=5,
            customer_id="AUTH_USER"
        )

        is_authenticated = order.customer_id != "INVALID"

        if is_authenticated:
            response = create_order(order)
            self.assertEqual(response["message"], "Order created")
        else:
            self.fail("User should be authenticated")

    def test_cannot_cancel_after_preparing(self):

        order = Order(
            order_id="9",
            restaurant_id=10,
            food_item="Burger",
            order_time="2025-03-11T12:00:00",
            order_value=15,
            delivery_method="bike",
            delivery_distance=5,
            customer_id="C9"
        )

        order.status = OrderStatus.PREPARING
        orders_db["9"] = order

        with self.assertRaises(ValueError):
            OrderService.cancel_order("9")

    def test_cancel_allowed_before_preparing(self):

        order = Order(
            order_id="10",
            restaurant_id=10,
            food_item="Pizza",
            order_time="2025-03-11T12:00:00",
            order_value=20,
            delivery_method="car",
            delivery_distance=4,
            customer_id="C10"
        )

        orders_db["10"] = order
        cancelled_order = OrderService.cancel_order("10")

        self.assertEqual(cancelled_order.status, OrderStatus.CANCELLED)

    def test_order_id_unique(self):

        order1 = OrderCreate(
            order_id="11",
            restaurant_id=10,
            food_item="Burger",
            order_time="2025-03-11T12:10:00",
            order_value=15,
            delivery_method="bike",
            delivery_distance=3,
            customer_id="C10"
        )

        order2 = OrderCreate(
            order_id="12",
            restaurant_id=10,
            food_item="Sushi",
            order_time="2025-03-11T12:20:00",
            order_value=25,
            delivery_method="car",
            delivery_distance=5,
            customer_id="C12"
        )

        OrderService.create_order(order1)
        OrderService.create_order(order2)

        self.assertIn("11", orders_db)
        self.assertIn("12", orders_db)
        self.assertNotEqual("11", "12")


if __name__ == "__main__":
    unittest.main()