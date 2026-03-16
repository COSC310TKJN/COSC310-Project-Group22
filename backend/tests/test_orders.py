import unittest
from pydantic import ValidationError
from models.order import Order, OrderStatus
from routes.order_routes import create_order
from schemas.order_schema import OrderCreate


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
 
    def test_eligibility(self):

        order = OrderCreate(
            order_id="3",
            restaurant_id=10,
            food_item="Pizza",
            order_time="2025-03-11T12:00:00",
            order_value=25,
            delivery_method="bike",
            delivery_distance=5,
            customer_id="C3"
        )

        response = create_order(order)

        self.assertEqual(response["message"], "Order created")
        self.assertIn("order", response)

    def test_invalid_order_value_type(self):

        with self.assertRaises(ValidationError):

            OrderCreate(
            order_id="4",
            restaurant_id=5,
            food_item="Burger",
            order_time="2025-03-11T12:00:00",
            order_value="twenty",
            delivery_method="car",
            delivery_distance=4,
            customer_id="C4"
        )


if __name__ == "__main__":
    unittest.main()