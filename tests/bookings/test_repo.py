import pytest
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.bookings.models import Booking
from src.bookings.repo import BookingRepository
from src.tours.models import Tour
from src.auth.models import User


async def test_get_all_bookings(db_async_session: AsyncSession, sample_booking_data):
    repository = BookingRepository(db_async_session)

    # Prepopulate the database with a sample booking
    booking = Booking(**sample_booking_data)
    db_async_session.add(booking)
    await db_async_session.commit()

    # Test retrieving all bookings
    bookings = await repository.get_all_bookings()
    assert len(bookings) > 0
    assert any(b.status == sample_booking_data["status"] for b in bookings)


async def test_get_booking_by_id(db_async_session: AsyncSession, sample_booking_data):
    repository = BookingRepository(db_async_session)

    # Prepopulate the database with a sample booking
    booking = Booking(**sample_booking_data)
    db_async_session.add(booking)
    await db_async_session.commit()
    await db_async_session.refresh(booking)

    # Test retrieving a booking by ID
    retrieved_booking = await repository.get_booking_by_id(booking.booking_id)
    assert retrieved_booking is not None
    assert retrieved_booking.booking_id == booking.booking_id
    assert retrieved_booking.status == booking.status


async def test_create_booking(db_async_session: AsyncSession, sample_booking_data):
    repository = BookingRepository(db_async_session)

    # Test creating a new booking
    created_booking = await repository.create_booking(sample_booking_data)
    assert created_booking is not None
    assert created_booking.status == sample_booking_data["status"]

    # Verify the booking exists in the database
    stmt = select(Booking).filter_by(booking_id=created_booking.booking_id)
    result = await db_async_session.execute(stmt)
    booking_in_db = result.scalar_one_or_none()
    assert booking_in_db is not None
    assert booking_in_db.status == sample_booking_data["status"]


async def test_update_booking(db_async_session: AsyncSession, sample_booking_data):
    repository = BookingRepository(db_async_session)

    # Prepopulate the database with a sample booking
    booking = Booking(**sample_booking_data)
    db_async_session.add(booking)
    await db_async_session.commit()
    await db_async_session.refresh(booking)

    # Test updating the booking
    update_data = {"status": "canceled"}
    updated_booking = await repository.update_booking(booking.booking_id, update_data)
    assert updated_booking is not None
    assert updated_booking.status == update_data["status"]


async def test_delete_booking(db_async_session: AsyncSession, sample_booking_data):
    repository = BookingRepository(db_async_session)

    # Prepopulate the database with a sample booking
    booking = Booking(**sample_booking_data)
    db_async_session.add(booking)
    await db_async_session.commit()
    await db_async_session.refresh(booking)

    # Test deleting the booking
    deleted_booking = await repository.delete_booking(booking.booking_id)
    assert deleted_booking is not None

    # Verify the booking no longer exists in the database
    stmt = select(Booking).filter_by(booking_id=booking.booking_id)
    result = await db_async_session.execute(stmt)
    booking_in_db = result.scalar_one_or_none()
    assert booking_in_db is None
