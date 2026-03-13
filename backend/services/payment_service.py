import uuid

from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.models.payment import Payment, PaymentMethod, PaymentStatus
from backend.repositories import payment_repo
from backend.schemas.payment_schema import PaymentRequest


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

    return payment_repo.create_payment(db, payment)


def get_available_methods():
    return [{"name": method.value, "label": method.name.replace("_", " ").title()} for method in PaymentMethod]


def _simulate_payment(method: PaymentMethod, amount: float) -> PaymentStatus:
    if amount > 10000:
        return PaymentStatus.FAILED
    return PaymentStatus.COMPLETED
