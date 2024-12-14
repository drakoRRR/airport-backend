import uuid

from sqlalchemy import Boolean, Column, DateTime, String, func, select, Date, Float, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from src.database import Base


class Tour(Base):
    """Model representing tours."""
    __tablename__ = "tours"

    tour_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    destination = Column(String, nullable=False)
    duration = Column(Integer, nullable=False)  # Duration in days
    cost = Column(Float, nullable=False)
    transport = Column(String, nullable=False)
    hotel = Column(String, nullable=False)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    bookings = relationship("Booking", back_populates="tour")