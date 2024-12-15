import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from src.auth.hashing import Hasher
from src.auth.models import User

USER_NAME = "john_junior"
EMAIL = "example@example.com"
PASSWORD = "qwerty1234"


async def create_test_user(session: AsyncSession):
    result = await session.execute(select(User).filter_by(user_name=USER_NAME, email=EMAIL))
    existing_user = result.scalars().first()

    if existing_user:
        return existing_user

    hashed_password = Hasher.get_password_hash(PASSWORD)
    test_user = User(
        user_name=USER_NAME,
        email=EMAIL,
        hashed_password=hashed_password,
        # full_name="John Doe",
        # birth_date=datetime.date(1900, 1, 1),
        # passport_data="10203021321",
        # phone_number="1234567890",
        # card_number="3282881902321325"
    )
    session.add(test_user)
    await session.commit()
    return test_user
