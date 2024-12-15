import pytest
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.tours.models import Tour
from src.tours.repo import TourRepository


@pytest.fixture
def sample_tour_data():
    return {
        "destination": "Paris",
        "duration": 7,
        "cost": 1200.00,
        "transport": "Plane",
        "hotel": "Hilton",
        "description": "Explore the beauty of Paris in this 7-day tour."
    }


async def test_get_all_tours(db_async_session: AsyncSession, sample_tour_data):
    repository = TourRepository(db_async_session)

    # Prepopulate the database with a sample tour
    tour = Tour(**sample_tour_data)
    db_async_session.add(tour)
    await db_async_session.commit()

    # Test retrieving all tours
    tours = await repository.get_all_tours()
    assert len(tours) > 0
    assert any(t.destination == sample_tour_data["destination"] for t in tours)


async def test_get_tour_by_id(db_async_session: AsyncSession, sample_tour_data):
    repository = TourRepository(db_async_session)

    # Prepopulate the database with a sample tour
    tour = Tour(**sample_tour_data)
    db_async_session.add(tour)
    await db_async_session.commit()
    await db_async_session.refresh(tour)

    # Test retrieving a tour by ID
    retrieved_tour = await repository.get_tour_by_id(tour.tour_id)
    assert retrieved_tour is not None
    assert retrieved_tour.tour_id == tour.tour_id
    assert retrieved_tour.destination == tour.destination


async def test_create_tour(db_async_session: AsyncSession, sample_tour_data):
    repository = TourRepository(db_async_session)

    # Test creating a new tour
    created_tour = await repository.create_tour(sample_tour_data)
    assert created_tour is not None
    assert created_tour.destination == sample_tour_data["destination"]

    # Verify the tour exists in the database
    stmt = select(Tour).filter_by(tour_id=created_tour.tour_id)
    result = await db_async_session.execute(stmt)
    tour_in_db = result.scalar_one_or_none()
    assert tour_in_db is not None
    assert tour_in_db.destination == sample_tour_data["destination"]


async def test_update_tour(db_async_session: AsyncSession, sample_tour_data):
    repository = TourRepository(db_async_session)

    # Prepopulate the database with a sample tour
    tour = Tour(**sample_tour_data)
    db_async_session.add(tour)
    await db_async_session.commit()
    await db_async_session.refresh(tour)

    # Test updating the tour
    update_data = {"destination": "London", "cost": 1500.00}
    updated_tour = await repository.update_tour(tour.tour_id, update_data)
    assert updated_tour is not None
    assert updated_tour.destination == update_data["destination"]
    assert updated_tour.cost == update_data["cost"]


async def test_delete_tour(db_async_session: AsyncSession, sample_tour_data):
    repository = TourRepository(db_async_session)

    # Prepopulate the database with a sample tour
    tour = Tour(**sample_tour_data)
    db_async_session.add(tour)
    await db_async_session.commit()
    await db_async_session.refresh(tour)

    # Test deleting the tour
    deleted_tour = await repository.delete_tour(tour.tour_id)
    assert deleted_tour is not None

    # Verify the tour no longer exists in the database
    stmt = select(Tour).filter_by(tour_id=tour.tour_id)
    result = await db_async_session.execute(stmt)
    tour_in_db = result.scalar_one_or_none()
    assert tour_in_db is None
