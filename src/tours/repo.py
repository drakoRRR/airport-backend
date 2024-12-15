from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.tours.models import Tour
from uuid import UUID


class TourRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all_tours(self):
        """Retrieve all tours."""
        result = await self.db.execute(select(Tour))
        return result.scalars().all()

    async def get_tour_by_id(self, tour_id: UUID):
        """Retrieve a specific tour by its ID."""
        result = await self.db.execute(select(Tour).filter(Tour.tour_id == tour_id))
        return result.scalar_one_or_none()

    async def create_tour(self, tour_data: dict):
        """Create a new tour."""
        tour = Tour(**tour_data)
        self.db.add(tour)
        await self.db.commit()
        await self.db.refresh(tour)
        return tour

    async def update_tour(self, tour_id: UUID, update_data: dict):
        """Update an existing tour."""
        tour = await self.get_tour_by_id(tour_id)
        if not tour:
            return None
        for key, value in update_data.items():
            setattr(tour, key, value)
        await self.db.commit()
        await self.db.refresh(tour)
        return tour

    async def delete_tour(self, tour_id: UUID):
        """Delete a tour by its ID."""
        tour = await self.get_tour_by_id(tour_id)
        if tour:
            await self.db.delete(tour)
            await self.db.commit()
        return tour
