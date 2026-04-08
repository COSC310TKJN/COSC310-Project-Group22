from datetime import datetime

from backend.repositories.coupon_repo import CouponRepository


class CouponService:

    @staticmethod
    def apply_coupon(code: str, total: float):

        coupon = CouponRepository.find_by_code(code)

        if not coupon:
            raise ValueError("Invalid coupon code")

        if coupon.expiry_date:

            expiry = datetime.strptime(coupon.expiry_date, "%Y-%m-%d")

            if datetime.now() > expiry:
                raise ValueError("Coupon expired")

        if total < coupon.min_order_value:
            raise ValueError("Order does not meet minimum value")

        if coupon.discount_type == "percent":

            discount = total * (coupon.discount_value / 100)

        elif coupon.discount_type == "fixed":

            discount = coupon.discount_value

        else:

            raise ValueError("Invalid discount type")

        final_total = max(total - discount, 0)

        return final_total