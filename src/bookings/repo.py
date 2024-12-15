from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.bookings.models import Booking
from uuid import UUID


class BookingRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all_bookings(self):
        """Retrieve all bookings."""
        result = await self.db.execute(select(Booking))
        return result.scalars().all()

    async def get_booking_by_id(self, booking_id: UUID):
        """Retrieve a specific booking by its ID."""
        result = await self.db.execute(select(Booking).filter(Booking.booking_id == booking_id))
        return result.scalar_one_or_none()

    async def create_booking(self, booking_data: dict):
        """Create a new booking."""
        booking = Booking(**booking_data)
        self.db.add(booking)
        await self.db.commit()
        await self.db.refresh(booking)
        return booking

    async def update_booking(self, booking_id: UUID, update_data: dict):
        """Update an existing booking."""
        booking = await self.get_booking_by_id(booking_id)
        if not booking:
            return None
        for key, value in update_data.items():
            setattr(booking, key, value)
        await self.db.commit()
        await self.db.refresh(booking)
        return booking

    async def delete_booking(self, booking_id: UUID):
        """Delete a booking by its ID."""
        booking = await self.get_booking_by_id(booking_id)
        if booking:
            await self.db.delete(booking)
            await self.db.commit()
        return booking
