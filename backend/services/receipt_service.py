import uuid

from fastapi import HTTPException

from backend.repositories import receipt_repo


def generate_receipt(payment):
    receipt_number = f"REC-{uuid.uuid4().hex[:10].upper()}"
    tax = round(payment["amount"] * 0.1, 2)
    total = round(payment["amount"] + tax, 2)

    data = {
        "payment_id": payment["id"],
        "order_id": payment["order_id"],
        "customer_id": payment["customer_id"],
        "receipt_number": receipt_number,
        "amount": payment["amount"],
        "tax": tax,
        "total": total,
        "payment_method": payment["payment_method"],
    }

    return receipt_repo.create_receipt(data)


def get_receipt_by_order(order_id):
    receipt = receipt_repo.get_receipt_by_order_id(order_id)
    if not receipt:
        raise HTTPException(status_code=404, detail="Receipt not found for this order")
    return receipt
