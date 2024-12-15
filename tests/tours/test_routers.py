import pytest
from uuid import uuid4
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.tours.models import Tour


@pytest.mark.asyncio
async def test_get_all_tours(client: AsyncClient, db_async_session: AsyncSession, sample_tour: Tour, jwt_token: str):
    response = await client.get(
        "/tours/",
        headers={"Authorization": f"Bearer {jwt_token}"}
    )
    assert response.status_code == 200
    tours = response.json()
    assert len(tours) > 0
    assert any(t["destination"] == sample_tour.destination for t in tours)


@pytest.mark.asyncio
async def test_get_tour_by_id(client: AsyncClient, db_async_session: AsyncSession, sample_tour: Tour, jwt_token: str):
    response = await client.get(
        f"/tours/{sample_tour.tour_id}",
        headers={"Authorization": f"Bearer {jwt_token}"}
    )
    assert response.status_code == 200
    retrieved_tour = response.json()
    assert retrieved_tour["tour_id"] == str(sample_tour.tour_id)
    assert retrieved_tour["destination"] == sample_tour.destination


@pytest.mark.asyncio
async def test_create_tour(client: AsyncClient, jwt_token: str):
    tour_data = {
        "destination": "London",
        "duration": 5,
        "cost": 1000.00,
        "transport": "Train",
        "hotel": "Ritz",
        "description": "Discover the charm of London in 5 days."
    }

    response = await client.post(
        "/tours/",
        json=tour_data,
        headers={"Authorization": f"Bearer {jwt_token}"}
    )
    assert response.status_code == 200
    created_tour = response.json()
    assert created_tour["destination"] == "London"


@pytest.mark.asyncio
async def test_update_tour(client: AsyncClient, sample_tour: Tour, jwt_token: str):
    update_data = {"destination": "New York", "cost": 1500.00}

    response = await client.put(
        f"/tours/{sample_tour.tour_id}",
        json=update_data,
        headers={"Authorization": f"Bearer {jwt_token}"}
    )
    assert response.status_code == 200
    updated_tour = response.json()
    assert updated_tour["destination"] == "New York"
    assert updated_tour["cost"] == 1500.00


@pytest.mark.asyncio
async def test_delete_tour(client: AsyncClient, db_async_session: AsyncSession, sample_tour: Tour, jwt_token: str):
    response = await client.delete(
        f"/tours/{sample_tour.tour_id}",
        headers={"Authorization": f"Bearer {jwt_token}"}
    )
    assert response.status_code == 200
    deleted_tour = response.json()
    assert deleted_tour["tour_id"] == str(sample_tour.tour_id)

    # Verify the tour no longer exists in the database
    stmt = select(Tour).filter_by(tour_id=sample_tour.tour_id)
    result = await db_async_session.execute(stmt)
    tour_in_db = result.scalar_one_or_none()
    assert tour_in_db is None
