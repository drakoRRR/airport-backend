import asyncio

import pytest

from src.config import DATABASE_TEST_ASYNC_URL, DATABASE_TEST_SYNC_URL
from typing import AsyncGenerator
from httpx import AsyncClient
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from src.main import fastapi_app
from src.database import Base, get_db
from src.auth.models import User
from src.bookings.models import Booking
from src.tours.models import Tour
from src.auth.services import create_token_pair


async_test_engine = create_async_engine(DATABASE_TEST_ASYNC_URL, future=True)
async_test_session = sessionmaker(async_test_engine, expire_on_commit=False, class_=AsyncSession)

sync_test_engine = create_engine(DATABASE_TEST_SYNC_URL, future=True)
sync_test_session = sessionmaker(autocommit=False, autoflush=False, bind=sync_test_engine)


@pytest.fixture(scope="session", autouse=True)
def test_db():
    """Create and drop the test database tables."""
    Base.metadata.create_all(bind=sync_test_engine)
    try:
        yield
    finally:
        Base.metadata.drop_all(bind=sync_test_engine)


async def test_get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting async session"""
    session: AsyncSession = async_test_session()
    try:
        yield session
    finally:
        await session.close()


@pytest.fixture(scope="session")
async def event_loop(request):
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def client():
    fastapi_app.dependency_overrides[get_db] = test_get_db
    async with AsyncClient(app=fastapi_app, base_url="http://test") as client:
        yield client
    fastapi_app.dependency_overrides.clear()


@pytest.fixture(scope="function")
async def db_async_session():
    async with async_test_session() as session:
        yield session


@pytest.fixture
async def sample_user(db_async_session: AsyncSession):
    result = await db_async_session.execute(select(User).filter_by(user_name="Test User", email="test@example.com"))
    existing_user = result.scalars().first()

    if existing_user:
        return existing_user
    user = User(user_id=uuid4(), user_name="Test User", email="test@example.com", hashed_password="hashed_password")
    db_async_session.add(user)
    await db_async_session.commit()
    await db_async_session.refresh(user)
    return user


@pytest.fixture
async def sample_tour(db_async_session: AsyncSession):
    result = await db_async_session.execute(select(Tour).filter_by(destination="Paris", transport="Plane"))
    existing = result.scalars().first()

    if existing:
        return existing

    tour = Tour(
        tour_id=uuid4(),
        destination="Paris",
        duration=7,
        cost=1200.00,
        transport="Plane",
        hotel="Hilton",
        description="Explore the beauty of Paris in this 7-day tour."
    )
    db_async_session.add(tour)
    await db_async_session.commit()
    await db_async_session.refresh(tour)
    return tour


@pytest.fixture
def sample_booking_data(sample_user, sample_tour):
    return {
        "client_id": sample_user.user_id,
        "tour_id": sample_tour.tour_id,
        "status": "confirmed"
    }


@pytest.fixture
def jwt_token(sample_user):
    tokens = create_token_pair(sample_user)
    return tokens.access


@pytest.fixture
async def sample_booking(db_async_session: AsyncSession, sample_user: User, sample_tour: Tour):
    result = await db_async_session.execute(
        select(Booking).filter_by(client_id=sample_user.user_id, tour_id=sample_tour.tour_id)
    )
    existing_booking = result.scalars().first()

    if existing_booking:
        return existing_booking

    booking = Booking(
        booking_id=uuid4(),
        client_id=sample_user.user_id,
        tour_id=sample_tour.tour_id,
        status="confirmed"
    )
    db_async_session.add(booking)
    await db_async_session.commit()
    await db_async_session.refresh(booking)
    return booking
