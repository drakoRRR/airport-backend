import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from src.database import get_db, redis_client
from src.bookings.repo import BookingRepository
from src.config import CACHE_EXPIRATION


booking_router = APIRouter()


@booking_router.get("/")
def get_all_bookings(db: Session = Depends(get_db)):
    cache_key = "all_bookings"
    cached_data = redis_client.get(cache_key)
    if cached_data:
        return json.loads(cached_data)

    repository = BookingRepository(db)
    bookings = repository.get_all_bookings()
    result = [booking.__dict__ for booking in bookings]
    for item in result:
        item.pop('_sa_instance_state', None)
    redis_client.setex(cache_key, CACHE_EXPIRATION, json.dumps(result))
    return result


@booking_router.get("/{booking_id}")
def get_booking_by_id(booking_id: UUID, db: Session = Depends(get_db)):
    cache_key = f"booking_{booking_id}"
    cached_data = redis_client.get(cache_key)
    if cached_data:
        return json.loads(cached_data)

    repository = BookingRepository(db)
    booking = repository.get_booking_by_id(booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    result = booking.__dict__
    result.pop('_sa_instance_state', None)
    redis_client.setex(cache_key, CACHE_EXPIRATION, json.dumps(result))
    return result


@booking_router.post("/")
def create_booking(booking_data: dict, db: Session = Depends(get_db)):
    repository = BookingRepository(db)
    new_booking = repository.create_booking(booking_data)
    redis_client.delete("all_bookings")  # Invalidate the cache for all bookings
    return new_booking


@booking_router.put("/{booking_id}")
def update_booking(booking_id: UUID, update_data: dict, db: Session = Depends(get_db)):
    repository = BookingRepository(db)
    updated_booking = repository.update_booking(booking_id, update_data)
    if not updated_booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    redis_client.delete("all_bookings")
    redis_client.delete(f"booking_{booking_id}")
    return updated_booking


@booking_router.delete("/{booking_id}")
def delete_booking(booking_id: UUID, db: Session = Depends(get_db)):
    repository = BookingRepository(db)
    deleted_booking = repository.delete_booking(booking_id)
    if not deleted_booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    redis_client.delete("all_bookings")
    redis_client.delete(f"booking_{booking_id}")
    return deleted_booking
