from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.schemas.payment_schema import PaymentRequest, PaymentResponse, PaymentStatusResponse
from backend.schemas.receipt_schema import ReceiptResponse
from backend.services import payment_service, receipt_service

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.get("/methods")
def get_payment_methods():
    return payment_service.get_available_methods()


@router.post("/", response_model=PaymentResponse, status_code=201)
def submit_payment(request: PaymentRequest, db: Session = Depends(get_db)):
    payment = payment_service.process_payment(db, request)
    return payment


@router.get("/{payment_id}", response_model=PaymentStatusResponse)
def get_payment(payment_id: int, db: Session = Depends(get_db)):
    return payment_service.get_payment_status(db, payment_id)


@router.get("/order/{order_id}", response_model=PaymentStatusResponse)
def get_order_payment(order_id: int, db: Session = Depends(get_db)):
    return payment_service.get_payment_by_order(db, order_id)


@router.get("/order/{order_id}/validate")
def validate_order_payment(order_id: int, db: Session = Depends(get_db)):
    return payment_service.validate_order_paid(db, order_id)


@router.get("/order/{order_id}/receipt", response_model=ReceiptResponse)
def get_order_receipt(order_id: int, db: Session = Depends(get_db)):
    return receipt_service.get_receipt_by_order(db, order_id)
