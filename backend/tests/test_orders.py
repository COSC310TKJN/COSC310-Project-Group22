import unittest
from models.order import Order, OrderStatus


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

    


if __name__ == "__main__":
    unittest.main()