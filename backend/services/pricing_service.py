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

    @staticmethod
    def calculate_estimated_price(base_price):
    if base_price < 0:
        raise ValueError("Base price cannot be negative")
    return round(base_price + PricingService.calc_tax(base_price), 2)

    
    @staticmethod
    def calculate_subtotal(order):

        if order.order_value < 0:
            raise ValueError("Order value cannot be negative")

        return order.order_value

    @staticmethod
    def calculate_subtotal_value(value):

        if value < 0:
            raise ValueError("Order value cannot be negative")

        return value

    @staticmethod
    def calc_total(order):

        subtotal = order.order_value

        delivery_fee = PricingService.calc_delivery_fee(
            order.delivery_method,
            order.delivery_distance
        )
        
        tax = PricingService.calc_tax(subtotal)


        total = subtotal + delivery_fee + tax

        return {
            "subtotal": subtotal,
            "delivery_fee": delivery_fee,
            "tax": round(tax, 2),
            "total": round(total, 2)
        }

    @staticmethod
    def calculate_total(order):

        return PricingService.calc_total(order)
