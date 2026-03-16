from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


def get_engine(db_url: str, debug: bool = False):
    return create_async_engine(db_url, echo=debug)


def get_session_factory(db_url: str, debug: bool = False):
    engine = get_engine(db_url, debug)
    return async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


def make_get_db(db_url: str, debug: bool = False):
    factory = get_session_factory(db_url, debug)

    async def get_db():
        async with factory() as session:
            yield session

    return get_db
