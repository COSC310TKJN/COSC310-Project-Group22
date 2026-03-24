class PricingService:

    TAX_RATE = 0.12
    BIKE_RATE = 1.0
    CAR_RATE = 1.5


    @staticmethod
    def calc_delivery_fee(delivery_method, distance):

        if delivery_method == "bike":
            rate = PricingService.BIKE_RATE
        else:
            rate = PricingService.CAR_RATE

        return rate * distance
    

    @staticmethod
    def calc_tax(order_value):

        return order_value * PricingService.TAX_RATE
