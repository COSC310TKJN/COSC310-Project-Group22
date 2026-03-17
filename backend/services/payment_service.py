import uuid

from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.models.payment import Payment, PaymentMethod, PaymentStatus
from backend.repositories import payment_repo
from backend.schemas.payment_schema import PaymentRequest
from backend.services import receipt_service


def process_payment(db: Session, request: PaymentRequest) -> Payment:
    existing = payment_repo.get_payment_by_order_id(db, request.order_id)
    if existing:
        raise HTTPException(status_code=400, detail="Payment already exists for this order")

    transaction_id = str(uuid.uuid4())

    simulated_status = _simulate_payment(request.payment_method, request.amount)

    payment = Payment(
        order_id=request.order_id,
        customer_id=request.customer_id,
        amount=request.amount,
        payment_method=request.payment_method.value,
        status=simulated_status.value,
        transaction_id=transaction_id,
    )

    payment = payment_repo.create_payment(db, payment)

    if payment.status == PaymentStatus.COMPLETED.value:
        receipt_service.generate_receipt(db, payment)

    return payment


def get_payment_status(db: Session, payment_id: int):
    payment = payment_repo.get_payment_by_id(db, payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment


def get_payment_by_order(db: Session, order_id: int):
    payment = payment_repo.get_payment_by_order_id(db, order_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found for this order")
    return payment


def get_available_methods():
    return [{"name": method.value, "label": method.name.replace("_", " ").title()} for method in PaymentMethod]


def validate_order_paid(db: Session, order_id: int):
    payment = payment_repo.get_payment_by_order_id(db, order_id)
    if not payment:
        return {"order_id": order_id, "is_paid": False, "message": "No payment found for this order"}
    if payment.status != PaymentStatus.COMPLETED.value:
        return {"order_id": order_id, "is_paid": False, "message": "Payment not completed"}
    return {"order_id": order_id, "is_paid": True, "message": "Payment completed"}


def get_paid_orders(db: Session):
    return payment_repo.get_payments_by_status(db, PaymentStatus.COMPLETED.value)


def get_failed_payments(db: Session):
    return payment_repo.get_payments_by_status(db, PaymentStatus.FAILED.value)


def _simulate_payment(method: PaymentMethod, amount: float) -> PaymentStatus:
    if amount > 10000:
        return PaymentStatus.FAILED
    return PaymentStatus.COMPLETED
