from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from backend.app.database import Base
from backend.models.order import OrderStatus

class OrderDB(Base):
  __tablename__ = "orders"
  
  id = Column(Integer, primary_key=True, index=True)
  customer_id = Column(String, nullable=False, index=True)
  current_status = Column(String, nullable=False, default=OrderStatus.CREATED.value)
  restaurant_id = Column(Integer, nullable=True)
  food_item = Column(String, nullable=True)
  order_value = Column(Float, nullable=True)
  order_time = Column(DateTime, server_default=func.now())
  update_time = Column(DateTime, server_default=func.now(), onupdate=func.now())

status_history = relationship(
        "DeliveryStatusUpdate",
        back_populates="order",
        order_by="DeliveryStatusUpdate.update_time",
    )

class DeliveryStatusUpdate(Base):

__tablename__ = "delivery_status_updates"

id = Column(Integer, primary_key=True, index=True)
order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
status = Column(String, nullable=False)
update_time = Column(DateTime, server_default=func.now())
updated_by = Column(String, nullable=True)

order = relationship("OrderDB", back_populates="status_history")
