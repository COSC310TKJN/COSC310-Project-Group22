class Coupon:

    def __init__(
        self,
        code: str,
        discount_type: str,
        discount_value: float,
        expiry_date: str = None,
        min_order_value: float = 0,
        one_time_use: bool = False
    ):
        self.code = code
        self.discount_type = discount_type
        self.discount_value = discount_value
        self.expiry_date = expiry_date
        self.min_order_value = min_order_value
        self.one_time_use = one_time_use