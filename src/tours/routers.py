import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from src.database import get_db, redis_client
from src.tours.repo import TourRepository
from src.config import CACHE_EXPIRATION


tours_router = APIRouter()


@tours_router.get("/")
def get_all_tours(db: Session = Depends(get_db)):
    cache_key = "all_tours"
    cached_data = redis_client.get(cache_key)
    if cached_data:
        return json.loads(cached_data)

    repository = TourRepository(db)
    tours = repository.get_all_tours()
    result = [tour.__dict__ for tour in tours]
    for item in result:
        item.pop('_sa_instance_state', None)
    redis_client.setex(cache_key, CACHE_EXPIRATION, json.dumps(result))
    return result


@tours_router.get("/{tour_id}")
def get_tour_by_id(tour_id: UUID, db: Session = Depends(get_db)):
    cache_key = f"tour_{tour_id}"
    cached_data = redis_client.get(cache_key)
    if cached_data:
        return json.loads(cached_data)

    repository = TourRepository(db)
    tour = repository.get_tour_by_id(tour_id)
    if not tour:
        raise HTTPException(status_code=404, detail="Tour not found")

    result = tour.__dict__
    result.pop('_sa_instance_state', None)
    redis_client.setex(cache_key, CACHE_EXPIRATION, json.dumps(result))
    return result


@tours_router.post("/")
def create_tour(tour_data: dict, db: Session = Depends(get_db)):
    repository = TourRepository(db)
    new_tour = repository.create_tour(tour_data)
    redis_client.delete("all_tours")  # Invalidate the cache for all tours
    return new_tour


@tours_router.put("/{tour_id}")
def update_tour(tour_id: UUID, update_data: dict, db: Session = Depends(get_db)):
    repository = TourRepository(db)
    updated_tour = repository.update_tour(tour_id, update_data)
    if not updated_tour:
        raise HTTPException(status_code=404, detail="Tour not found")

    redis_client.delete("all_tours")
    redis_client.delete(f"tour_{tour_id}")
    return updated_tour


@tours_router.delete("/{tour_id}")
def delete_tour(tour_id: UUID, db: Session = Depends(get_db)):
    repository = TourRepository(db)
    deleted_tour = repository.delete_tour(tour_id)
    if not deleted_tour:
        raise HTTPException(status_code=404, detail="Tour not found")

    redis_client.delete("all_tours")
    redis_client.delete(f"tour_{tour_id}")
    return deleted_tour
