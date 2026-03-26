import uuid

from fastapi import HTTPException

from backend.models.payment import PaymentMethod, PaymentStatus
from backend.repositories import payment_repo
from backend.services import receipt_service


def process_payment(request) -> dict:
    existing = payment_repo.get_payment_by_order_id(request.order_id)
    if existing:
        raise HTTPException(status_code=400, detail="Payment already exists for this order")

    transaction_id = str(uuid.uuid4())
    simulated_status = _simulate_payment(request.payment_method, request.amount)

    data = {
        "order_id": request.order_id,
        "customer_id": request.customer_id,
        "amount": request.amount,
        "payment_method": request.payment_method.value,
        "status": simulated_status.value,
        "transaction_id": transaction_id,
    }

    payment = payment_repo.create_payment(data)

    if payment["status"] == PaymentStatus.COMPLETED.value:
        receipt_service.generate_receipt(payment)

    return payment


def get_payment_status(payment_id: int) -> dict:
    payment = payment_repo.get_payment_by_id(payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment


def get_payment_by_order(order_id: int) -> dict:
    payment = payment_repo.get_payment_by_order_id(order_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found for this order")
    return payment


def get_available_methods() -> list[dict]:
    return [{"name": m.value, "label": m.name.replace("_", " ").title()}
            for m in PaymentMethod]


def validate_order_paid(order_id: int) -> dict:
    payment = payment_repo.get_payment_by_order_id(order_id)
    if not payment:
        return {"order_id": order_id, "is_paid": False,
                "message": "No payment found for this order"}
    if payment["status"] != PaymentStatus.COMPLETED.value:
        return {"order_id": order_id, "is_paid": False,
                "message": "Payment not completed"}
    return {"order_id": order_id, "is_paid": True,
            "message": "Payment completed"}


def get_paid_orders() -> list[dict]:
    return payment_repo.get_payments_by_status(PaymentStatus.COMPLETED.value)


def get_failed_payments() -> list[dict]:
    return payment_repo.get_payments_by_status(PaymentStatus.FAILED.value)


def _simulate_payment(method: str, amount: float) -> PaymentStatus:
    if amount > 10000:
        return PaymentStatus.FAILED
    return PaymentStatus.COMPLETED
