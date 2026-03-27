import pytest
from httpx import AsyncClient
from fastapi import Depends
from travelhub_common.factory import create_app
from travelhub_common.testing import create_test_client


async def fake_get_db():
    yield object()


@pytest.fixture
def app():
    return create_app("test-service")


@pytest.mark.anyio
async def test_create_test_client_yields_async_client(app):
    async for client in create_test_client(app, fake_get_db):
        assert isinstance(client, AsyncClient)


@pytest.mark.anyio
async def test_create_test_client_overrides_dependency(app):
    async for client in create_test_client(app, fake_get_db):
        assert fake_get_db in app.dependency_overrides


@pytest.mark.anyio
async def test_create_test_client_clears_overrides_after(app):
    gen = create_test_client(app, fake_get_db)
    async for _ in gen:
        pass
    assert len(app.dependency_overrides) == 0
