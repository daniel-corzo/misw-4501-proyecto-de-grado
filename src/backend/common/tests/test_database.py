import inspect
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker
from travelhub_common.database import Base, get_engine, get_session_factory, make_get_db

DB_URL = "postgresql+asyncpg://user:pass@localhost/db"


def test_base_is_declarative_base():
    assert hasattr(Base, "metadata")
    assert hasattr(Base, "registry")


def test_get_engine_returns_async_engine():
    engine = get_engine(DB_URL)
    assert isinstance(engine, AsyncEngine)


def test_get_engine_with_debug():
    engine = get_engine(DB_URL, debug=True)
    assert isinstance(engine, AsyncEngine)


def test_get_session_factory_returns_sessionmaker():
    factory = get_session_factory(DB_URL)
    assert isinstance(factory, async_sessionmaker)


def test_make_get_db_returns_callable():
    get_db = make_get_db(DB_URL)
    assert callable(get_db)
    assert inspect.isasyncgenfunction(get_db)
