from datetime import datetime

payments = []
_next_id = 0


def _get_next_id():
    global _next_id
    _next_id += 1
    return _next_id


def create_payment(data):
    data["id"] = _get_next_id()
    data["created_at"] = datetime.now().isoformat()
    data["updated_at"] = datetime.now().isoformat()
    payments.append(data)
    return data


def get_payment_by_id(payment_id):
    for p in payments:
        if p["id"] == payment_id:
            return p
    return None


def get_payment_by_order_id(order_id):
    for p in payments:
        if p["order_id"] == order_id:
            return p
    return None


def get_payments_by_status(status):
    return [p for p in payments if p["status"] == status]


def clear():
    global _next_id
    payments.clear()
    _next_id = 0
