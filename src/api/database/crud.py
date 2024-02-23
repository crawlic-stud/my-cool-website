from typing import TypeVar

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import SQLModel, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.sql._typing import ColumnExpressionArgument

from . import db_utils

try:
    from tables.base import IntBasicModel
    from settings import db
    import exceptions
except ImportError:  # for alembic to work
    from ..tables.base import IntBasicModel
    from ..settings import db
    from .. import exceptions

T = TypeVar("T")

DB_URL = f"postgresql+asyncpg://{db.POSTGRES_USER}:{db.POSTGRES_PASSWORD}@{db.POSTGRES_HOST}/{db.POSTGRES_DB}"
DB_URL_SYNC = DB_URL.replace("+asyncpg", "")

DEFAULT_LIMIT = 20

engine = create_async_engine(DB_URL, echo=False, future=True, pool_pre_ping=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)  # type: ignore


async def get_async_session() -> AsyncSession:  # type: ignore
    async with async_session() as session:  # type: ignore
        yield session  # type: ignore


async def get_all(
    session: AsyncSession,
    db_table_type: type[SQLModel],
    offset: int = 0,
    limit: int = DEFAULT_LIMIT,
) -> list[SQLModel]:
    statement = select(db_table_type).offset(offset).limit(limit)
    res = await session.exec(statement)
    await session.commit()
    return list(res.all())


async def get_by_id(
    _id: int, session: AsyncSession, db_table_type: type[IntBasicModel]
) -> SQLModel:
    return await get_first_where(
        session,
        db_table_type,
        db_table_type.id == _id,
        f"ID={_id} doesn't exist for table={db_table_type.__name__}",
    )


async def get_first_where(
    session: AsyncSession,
    db_table_type: type[SQLModel],
    where: ColumnExpressionArgument[bool] | bool,
    error_msg: str | None = None,
) -> SQLModel:
    statement = select(db_table_type).where(where)
    res = await session.exec(statement)
    item = res.first()
    if item is None:
        if error_msg is None:
            error_msg = f"Item not found for table={db_table_type.__name__}"
        raise exceptions.NotFound(detail=error_msg)
    return item


async def delete_by_id(
    _id: int, session: AsyncSession, db_table_type: type[SQLModel]
) -> SQLModel:
    item = await get_by_id(_id, session, db_table_type)
    await session.delete(item)
    await session.commit()
    return item


async def update_by_id(
    _id: int,
    session: AsyncSession,
    data: SQLModel,
    db_table_type: type[SQLModel],
) -> SQLModel:
    item = await get_by_id(_id, session, db_table_type)
    new_item = db_utils.update_partially(item, data)
    session.add(new_item)
    await session.commit()
    await session.refresh(new_item)
    return new_item


async def create(
    item: SQLModel, session: AsyncSession, db_table_type: type[SQLModel]
) -> SQLModel:
    try:
        new_item = db_table_type(**item.dict())
        session.add(new_item)
        await session.commit()
        await session.refresh(new_item)
        return new_item
    except IntegrityError as e:
        raise exceptions.Conflict(
            detail=f"Integrity error.{db_utils.parse_integrity_error(str(e))}"
        )


async def upsert(
    item: IntBasicModel,
    session: AsyncSession,
    db_table_type: type[IntBasicModel],
    index_elements: list[str],
) -> SQLModel:
    stmt = (
        insert(db_table_type)
        .values(**item.model_dump())
        .on_conflict_do_update(index_elements=index_elements, set_=item.model_dump())
    )
    await session.exec(stmt)
    await session.commit()
    return item
