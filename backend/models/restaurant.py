from sqlalchemy import Column, Float, Integer, String

from backend.app.database import Base


class Restaurant(Base):
    __tablename__ = "restaurants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    cuisine_type = Column(String, nullable=False, index=True)
    address = Column(String, nullable=True)
