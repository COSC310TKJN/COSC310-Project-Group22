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
            code_key = (row.get("code") or "").strip().upper()
            if not code_key:
                continue
            exp = (row.get("expiry_date") or "").strip() or None
            coupon = Coupon(
                code=code_key,
                discount_type=(row.get("discount_type") or "percent").strip().lower(),
                discount_value=float(row["discount_value"]),
                expiry_date=exp,
                min_order_value=float(row.get("min_order_value") or 0),
                one_time_use=str(row.get("one_time_use", "")).strip().lower()
                in ("true", "1", "yes"),
            )

            coupons[code_key] = coupon

    return coupons


coupons_db = load_coupons()


class CouponRepository:

    @staticmethod
    def find_by_code(code: str):
        if not code or not str(code).strip():
            return None
        return coupons_db.get(str(code).strip().upper())