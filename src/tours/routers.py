import json
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from src.database import get_db, redis_client
from src.tours.repo import TourRepository
from src.config import CACHE_EXPIRATION
from src.auth.services import get_current_user
from src.auth.models import User


tours_router = APIRouter()


def serialize_tour(tour):
    """Helper function to serialize a Tour object."""
    return {
        "tour_id": str(tour.tour_id),
        "destination": tour.destination,
        "duration": tour.duration,
        "cost": tour.cost,
        "transport": tour.transport,
        "hotel": tour.hotel,
        "description": tour.description,
        "created_at": tour.created_at.isoformat() if isinstance(tour.created_at, datetime) else None,
        "updated_at": tour.updated_at.isoformat() if isinstance(tour.updated_at, datetime) else None,
    }


@tours_router.get("/")
async def get_all_tours(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    cache_key = "all_tours"
    cached_data = await redis_client.get(cache_key)
    if cached_data:
        return json.loads(cached_data.decode("utf-8"))

    repository = TourRepository(db)
    tours = await repository.get_all_tours()
    result = [serialize_tour(tour) for tour in tours]
    await redis_client.setex(cache_key, CACHE_EXPIRATION, json.dumps(result))
    return result


@tours_router.get("/{tour_id}")
async def get_tour_by_id(
    tour_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    cache_key = f"tour_{tour_id}"
    cached_data = await redis_client.get(cache_key)
    if cached_data:
        return json.loads(cached_data.decode("utf-8"))

    repository = TourRepository(db)
    tour = await repository.get_tour_by_id(tour_id)
    if not tour:
        raise HTTPException(status_code=404, detail="Tour not found")

    result = serialize_tour(tour)
    await redis_client.setex(cache_key, CACHE_EXPIRATION, json.dumps(result))
    return result


@tours_router.post("/")
async def create_tour(
    tour_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    repository = TourRepository(db)
    new_tour = await repository.create_tour(tour_data)
    await redis_client.delete("all_tours")  # Invalidate the cache for all tours
    return new_tour


@tours_router.put("/{tour_id}")
async def update_tour(
    tour_id: UUID,
    update_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    repository = TourRepository(db)
    updated_tour = await repository.update_tour(tour_id, update_data)
    if not updated_tour:
        raise HTTPException(status_code=404, detail="Tour not found")

    await redis_client.delete("all_tours")
    await redis_client.delete(f"tour_{tour_id}")
    return updated_tour


@tours_router.delete("/{tour_id}")
async def delete_tour(
    tour_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    repository = TourRepository(db)
    deleted_tour = await repository.delete_tour(tour_id)
    if not deleted_tour:
        raise HTTPException(status_code=404, detail="Tour not found")

    await redis_client.delete("all_tours")
    await redis_client.delete(f"tour_{tour_id}")
    return deleted_tour
