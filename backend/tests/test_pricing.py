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


def test_tax_calculation():

    tax = PricingService.calc_tax(100)

    assert tax == 12


def test_tax_zero():

    tax = PricingService.calc_tax(0)

    assert tax == 0


def test_tax_decimal():

    tax = PricingService.calc_tax(20)

    assert tax == 2.4
