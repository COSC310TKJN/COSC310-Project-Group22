import pytest
from backend.models.order import Order
from backend.services.pricing_service import PricingService
from backend.services.order_service import OrderService
from backend.schemas.order_schema import OrderCreate


def test_bike_delivery_fee():

    fee = PricingService.calc_delivery_fee("bike", 5)

    assert fee == 5


def test_car_delivery_fee():

    fee = PricingService.calc_delivery_fee("car", 4)

    assert fee == 6


def test_car_default_case():

    fee = PricingService.calc_delivery_fee("car", 2)

    assert fee == 3


def test_tax_calculation():

    tax = PricingService.calc_tax(100)

    assert tax == 12


def test_tax_zero():

    tax = PricingService.calc_tax(0)

    assert tax == 0


def test_tax_decimal():

    tax = PricingService.calc_tax(20)

    assert tax == 2.4


def test_calculate_total():

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

    result = PricingService.calculate_total(order)

    assert result["subtotal"] == 20
    assert result["delivery_fee"] == 5
    assert result["tax"] == 2.4
    assert result["total"] == 27.4


def test_subtotal_valid():

    order = Order(
        order_id="2",
        restaurant_id=10,
        food_item="Pizza",
        order_time="2025-03-11T12:00:00",
        order_value=30,
        delivery_method="car",
        delivery_distance=5,
        customer_id="C2"
    )

    assert PricingService.calculate_subtotal(order) == 30


def test_subtotal_negative():

    with pytest.raises(ValueError):
        PricingService.calculate_subtotal_value(-5)


def test_car_delivery_total():

    order = Order(
        order_id="4",
        restaurant_id=10,
        food_item="Burger",
        order_time="2025-03-11T12:00:00",
        order_value=30,
        delivery_method="car",
        delivery_distance=4,
        customer_id="C4"
    )

    result = PricingService.calc_total(order)

    assert result["delivery_fee"] == 6
    assert round(result["tax"], 2) == 3.6
    assert result["total"] == 39.6


def test_zero_distance():

    order = Order(
        order_id="5",
        restaurant_id=10,
        food_item="Salad",
        order_time="2025-03-11T12:00:00",
        order_value=15,
        delivery_method="bike",
        delivery_distance=0,
        customer_id="C5"
    )

    result = PricingService.calc_total(order)

    assert result["delivery_fee"] == 0
    assert result["total"] == 16.8


def test_order_pricing_integration():

    order_data = OrderCreate(
        order_id="6",
        restaurant_id=10,
        food_item="Pizza",
        order_time="2025-03-11T12:00:00",
        order_value=25,
        delivery_method="car",
        delivery_distance=5,
        customer_id="C6"
    )

    order = OrderService.create_order(order_data)

    result = PricingService.calc_total(order)

    assert result["subtotal"] == 25
    assert result["delivery_fee"] == 7.5
    assert result["tax"] == 3.0
    assert result["total"] == 35.5