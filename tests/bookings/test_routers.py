import pytest
from uuid import uuid4
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.bookings.models import Booking
from src.bookings.repo import BookingRepository
from src.tours.models import Tour
from src.auth.models import User

from tests.auth.utils import create_test_user, USER_NAME, PASSWORD


async def test_get_all_bookings(client: AsyncClient, db_async_session: AsyncSession, sample_booking: Booking, jwt_token: str):
    response = await client.get(
        "/bookings/",
        headers={"Authorization": f"Bearer {jwt_token}"}
    )
    assert response.status_code == 200
    bookings = response.json()
    assert len(bookings) > 0
    assert any(b["status"] == sample_booking.status for b in bookings)


async def test_get_booking_by_id(client: AsyncClient, db_async_session: AsyncSession, sample_booking: Booking, jwt_token: str):
    response = await client.get(
        f"/bookings/{sample_booking.booking_id}",
        headers={"Authorization": f"Bearer {jwt_token}"}
    )
    assert response.status_code == 200
    retrieved_booking = response.json()
    assert retrieved_booking["booking_id"] == str(sample_booking.booking_id)
    assert retrieved_booking["status"] == sample_booking.status


async def test_create_booking(client: AsyncClient, sample_user: User, sample_tour: Tour, jwt_token: str):
    booking_data = {
        "client_id": str(sample_user.user_id),
        "tour_id": str(sample_tour.tour_id),
        "status": "confirmed"
    }

    response = await client.post(
        "/bookings/",
        json=booking_data,
        headers={"Authorization": f"Bearer {jwt_token}"}
    )
    assert response.status_code == 200
    created_booking = response.json()
    assert created_booking["status"] == "confirmed"


async def test_update_booking(client: AsyncClient, sample_booking: Booking, jwt_token: str):
    update_data = {"status": "canceled"}

    response = await client.put(
        f"/bookings/{sample_booking.booking_id}",
        json=update_data,
        headers={"Authorization": f"Bearer {jwt_token}"}
    )
    assert response.status_code == 200
    updated_booking = response.json()
    assert updated_booking["status"] == "canceled"


async def test_delete_booking(client: AsyncClient, db_async_session: AsyncSession, sample_booking: Booking, jwt_token: str):
    response = await client.delete(
        f"/bookings/{sample_booking.booking_id}",
        headers={"Authorization": f"Bearer {jwt_token}"}
    )
    assert response.status_code == 200
    deleted_booking = response.json()
    assert deleted_booking["booking_id"] == str(sample_booking.booking_id)

    # Verify the booking no longer exists in the database
    stmt = select(Booking).filter_by(booking_id=sample_booking.booking_id)
    result = await db_async_session.execute(stmt)
    booking_in_db = result.scalar_one_or_none()
    assert booking_in_db is None
