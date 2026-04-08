import csv
import os
from pathlib import Path

from backend.models.coupon import Coupon


COUPON_HEADERS = [
    "code",
    "discount_type",
    "discount_value",
    "expiry_date",
    "min_order_value",
    "one_time_use"
]


def get_coupon_path():
    return Path(os.environ.get("COUPONS_CSV_PATH", "data/coupons.csv"))


def load_coupons():

    path = get_coupon_path()

    if not path.exists():
        return {}

    coupons = {}

    with open(path, newline="", encoding="utf-8") as f:

        reader = csv.DictReader(f)

        for row in reader:

            coupon = Coupon(
                code=row["code"],
                discount_type=row["discount_type"],
                discount_value=float(row["discount_value"]),
                expiry_date=row["expiry_date"],
                min_order_value=float(row["min_order_value"]),
                one_time_use=row["one_time_use"] == "True"
            )

            coupons[coupon.code] = coupon

    return coupons


coupons_db = load_coupons()


class CouponRepository:

    @staticmethod
    def find_by_code(code: str):

        return coupons_db.get(code)