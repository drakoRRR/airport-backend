from sqlalchemy.orm import Session
from src.tours.models import Tour
from uuid import UUID


class TourRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all_tours(self):
        """Retrieve all tours."""
        return self.db.query(Tour).all()

    def get_tour_by_id(self, tour_id: UUID):
        """Retrieve a specific tour by its ID."""
        return self.db.query(Tour).filter(Tour.tour_id == tour_id).first()

    def create_tour(self, tour_data: dict):
        """Create a new tour."""
        tour = Tour(**tour_data)
        self.db.add(tour)
        self.db.commit()
        self.db.refresh(tour)
        return tour

    def update_tour(self, tour_id: UUID, update_data: dict):
        """Update an existing tour."""
        tour = self.get_tour_by_id(tour_id)
        if not tour:
            return None
        for key, value in update_data.items():
            setattr(tour, key, value)
        self.db.commit()
        self.db.refresh(tour)
        return tour

    def delete_tour(self, tour_id: UUID):
        """Delete a tour by its ID."""
        tour = self.get_tour_by_id(tour_id)
        if tour:
            self.db.delete(tour)
            self.db.commit()
        return tour
