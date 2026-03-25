from datetime import datetime

receipts = []
_next_id = 0


def _get_next_id():
    global _next_id
    _next_id += 1
    return _next_id


def create_receipt(data):
    data["id"] = _get_next_id()
    data["issued_at"] = datetime.now().isoformat()
    receipts.append(data)
    return data


def get_receipt_by_order_id(order_id):
    for r in receipts:
        if r["order_id"] == order_id:
            return r
    return None


def clear():
    global _next_id
    receipts.clear()
    _next_id = 0
