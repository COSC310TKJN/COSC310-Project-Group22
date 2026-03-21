import unittest
from pydantic import ValidationError
import pytest
from models.order import Order, OrderStatus
from routes.order_routes import create_order
from schemas.order_schema import OrderCreate
from services.order_service import OrderService, orders_db


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
            
    @staticmethod
    def create_order(order_data):

        if order_data.customer_id == "INVALID":
            raise ValueError("Customer is not eligible")

        order = Order(
            order_id=order_data.order_id,
            restaurant_id=order_data.restaurant_id,
            food_item=order_data.food_item,
            order_time=order_data.order_time,
            order_value=order_data.order_value,
            delivery_method=order_data.delivery_method,
            delivery_distance=order_data.delivery_distance,
            customer_id=order_data.customer_id,
            traffic_condition=order_data.traffic_condition,
            weather_condition=order_data.weather_condition,
            route_taken=order_data.route_taken
        )

        orders_db[order.order_id] = order
        return order


    def test_unauthenticated_user_pytest():

        order = OrderCreate(
            order_id="10",
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
            order_id="11",
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


if __name__ == "__main__":
    unittest.main()