from sqlalchemy import Boolean, Column, Integer, String

from backend.app.database import Base


class NotificationPreference(Base):
    __tablename__ = "notification_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=False, index=True)
    notification_type = Column(String, nullable=False)
    enabled = Column(Boolean, default=True)
    channel = Column(String, default="in_app")
