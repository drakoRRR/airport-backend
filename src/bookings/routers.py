import json

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from src.database import get_db, redis_client
from src.bookings.repo import BookingRepository
from src.config import CACHE_EXPIRATION
from src.auth.services import get_current_user
from src.auth.models import User

booking_router = APIRouter()


def serialize_booking(booking):
    """Helper function to serialize a Booking object."""
    return {
        "booking_id": str(booking.booking_id),
        "client_id": str(booking.client_id),
        "tour_id": str(booking.tour_id),
        "status": booking.status,
        "booking_date": booking.booking_date.isoformat() if isinstance(booking.booking_date, datetime) else None
    }


@booking_router.get("/")
async def get_all_bookings(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    cache_key = "all_bookings"
    cached_data = await redis_client.get(cache_key)
    if cached_data:
        return json.loads(cached_data.decode("utf-8"))

    repository = BookingRepository(db)
    bookings = await repository.get_all_bookings()
    result = [serialize_booking(booking) for booking in bookings]
    await redis_client.setex(cache_key, CACHE_EXPIRATION, json.dumps(result))
    return result


@booking_router.get("/{booking_id}")
async def get_booking_by_id(
    booking_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    cache_key = f"booking_{booking_id}"
    cached_data = await redis_client.get(cache_key)
    if cached_data:
        return json.loads(cached_data.decode("utf-8"))

    repository = BookingRepository(db)
    booking = await repository.get_booking_by_id(booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    result = serialize_booking(booking)
    await redis_client.setex(cache_key, CACHE_EXPIRATION, json.dumps(result))
    return result


@booking_router.post("/")
async def create_booking(
    booking_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    repository = BookingRepository(db)
    booking_data["client_id"] = str(current_user.user_id)
    new_booking = await repository.create_booking(booking_data)
    redis_client.delete("all_bookings")  # Invalidate the cache for all bookings
    return new_booking


@booking_router.put("/{booking_id}")
async def update_booking(
    booking_id: UUID,
    update_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    repository = BookingRepository(db)
    updated_booking = await repository.update_booking(booking_id, update_data)
    if not updated_booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    redis_client.delete("all_bookings")
    redis_client.delete(f"booking_{booking_id}")
    return updated_booking


@booking_router.delete("/{booking_id}")
async def delete_booking(
    booking_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    repository = BookingRepository(db)
    deleted_booking = await repository.delete_booking(booking_id)
    if not deleted_booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    redis_client.delete("all_bookings")
    redis_client.delete(f"booking_{booking_id}")
    return deleted_booking
