import pytest
from backend.services.pricing_service import PricingService


def test_bike_delivery_fee():

    fee = PricingService.calc_delivery_fee("bike", 5)

    assert fee == 5


def test_car_delivery_fee():

    fee = PricingService.calc_delivery_fee("car", 4)

    assert fee == 6


def test_car_default_case():

    fee = PricingService.calc_delivery_fee("car", 2)

    assert fee == 3