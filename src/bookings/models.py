import uuid

from sqlalchemy import Boolean, Column, DateTime, String, func, select, Date, Float, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.database import Base


class Booking(Base):
    """Model representing bookings."""
    __tablename__ = "bookings"

    booking_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    client_id = Column(UUID(as_uuid=True), ForeignKey('user.user_id'), nullable=False)
    tour_id = Column(UUID(as_uuid=True), ForeignKey('tours.tour_id'), nullable=False)
    booking_date = Column(DateTime, default=func.now())
    status = Column(String, nullable=False, default="confirmed")  # confirmed, canceled, etc.

    client = relationship("User", back_populates="bookings")
    tour = relationship("Tour", back_populates="bookings")
