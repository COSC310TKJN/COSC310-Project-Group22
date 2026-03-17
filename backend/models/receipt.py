from sqlalchemy import Column, DateTime, Float, Integer, String
from sqlalchemy.sql import func

from backend.app.database import Base


class Receipt(Base):
    __tablename__ = "receipts"

    id = Column(Integer, primary_key=True, index=True)
    payment_id = Column(Integer, unique=True, nullable=False)
    order_id = Column(Integer, nullable=False)
    customer_id = Column(String, nullable=False)
    receipt_number = Column(String, unique=True, nullable=False)
    amount = Column(Float, nullable=False)
    tax = Column(Float, nullable=False)
    total = Column(Float, nullable=False)
    payment_method = Column(String, nullable=False)
    issued_at = Column(DateTime, server_default=func.now())
