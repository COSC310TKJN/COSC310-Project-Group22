from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.schemas.payment_schema import PaymentRequest, PaymentResponse, PaymentStatusResponse
from backend.schemas.receipt_schema import ReceiptResponse
from backend.services import payment_service, receipt_service
from backend.app.routes.auth_routes import require_manager
from backend.models.user import User


router = APIRouter(prefix="/payments", tags=["Payments"])


@router.get("/methods")
def get_payment_methods():
    return payment_service.get_available_methods()


@router.post("/", response_model=PaymentResponse, status_code=201)
def submit_payment(request: PaymentRequest, db: Session = Depends(get_db)):
    payment = payment_service.process_payment(db, request)
    return payment


@router.get("/order/{order_id}", response_model=PaymentStatusResponse)
def get_order_payment(order_id: int, db: Session = Depends(get_db)):
    return payment_service.get_payment_by_order(db, order_id)


@router.get("/order/{order_id}/validate")
def validate_order_payment(order_id: int, db: Session = Depends(get_db)):
    return payment_service.validate_order_paid(db, order_id)


@router.get("/order/{order_id}/receipt", response_model=ReceiptResponse)
def get_order_receipt(order_id: int, db: Session = Depends(get_db)):
    return receipt_service.get_receipt_by_order(db, order_id)


@router.get("/manager/orders")
def get_paid_orders(db: Session = Depends(get_db),
                    current_user: User = Depends(require_manager)):
    payments = payment_service.get_paid_orders(db)
    return [{"order_id": p.order_id, "amount": p.amount, "status": p.status} for p in payments]


@router.get("/manager/failed-payments")
def get_failed_payments(db: Session = Depends(get_db),
                        current_user: User = Depends(require_manager)):
    payments = payment_service.get_failed_payments(db)
    return [{"order_id": p.order_id, "amount": p.amount, "status": p.status, "transaction_id": p.transaction_id} for p in payments]


@router.get("/{payment_id}", response_model=PaymentStatusResponse)
def get_payment(payment_id: int, db: Session = Depends(get_db)):
    return payment_service.get_payment_status(db, payment_id)
