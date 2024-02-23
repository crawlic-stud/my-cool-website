from typing import Optional
from fastapi import HTTPException
from sqlmodel import select, update
from sqlmodel.ext.asyncio.session import AsyncSession

from tables.user import User
from database import crud


async def get_user_by_username(
    username: str | None, session: AsyncSession
) -> Optional[User]:
    if username is None:
        return
    statement = select(User).where(User.username == username)
    res = await session.exec(statement)
    return res.first()


async def create_user_if_not_exists(
    username: str, hashed_password: str, session: AsyncSession
) -> User:
    user = User(username=username, hashed_password=hashed_password)
    user: User = await crud.create(user, session, User)  # type: ignore
    return user


async def update_user_password(
    username: str, new_hashed_password: str, session: AsyncSession
) -> None:
    stmt = (
        update(User)
        .where(User.username == username)
        .values(hashed_password=new_hashed_password)
    )
    await session.exec(stmt)
    await session.commit()


async def create_superuser(username: str, hashed_password: str, session: AsyncSession):
    try:
        await create_user_if_not_exists(
            username,
            hashed_password,
            session,
        )
    except HTTPException:
        pass
