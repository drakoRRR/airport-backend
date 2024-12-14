from sqlalchemy.orm import Session
from src.bookings.models import Booking
from uuid import UUID


class BookingRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all_bookings(self):
        """Retrieve all bookings."""
        return self.db.query(Booking).all()

    def get_booking_by_id(self, booking_id: UUID):
        """Retrieve a specific booking by its ID."""
        return self.db.query(Booking).filter(Booking.booking_id == booking_id).first()

    def create_booking(self, booking_data: dict):
        """Create a new booking."""
        booking = Booking(**booking_data)
        self.db.add(booking)
        self.db.commit()
        self.db.refresh(booking)
        return booking

    def update_booking(self, booking_id: UUID, update_data: dict):
        """Update an existing booking."""
        booking = self.get_booking_by_id(booking_id)
        if not booking:
            return None
        for key, value in update_data.items():
            setattr(booking, key, value)
        self.db.commit()
        self.db.refresh(booking)
        return booking

    def delete_booking(self, booking_id: UUID):
        """Delete a booking by its ID."""
        booking = self.get_booking_by_id(booking_id)
        if booking:
            self.db.delete(booking)
            self.db.commit()
        return booking
