import pytest
import uuid
from httpx import AsyncClient, ASGITransport
from travelhub_common.factory import create_app


@pytest.fixture
def app():
    return create_app("test-service")


@pytest.mark.anyio
async def test_middleware_adds_correlation_id_header(app):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")
    assert "x-correlation-id" in response.headers


@pytest.mark.anyio
async def test_middleware_propagates_provided_correlation_id(app):
    corr_id = "my-custom-correlation-id"
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health", headers={"x-correlation-id": corr_id})
    assert response.headers["x-correlation-id"] == corr_id


@pytest.mark.anyio
async def test_middleware_generates_uuid_correlation_id(app):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")
    corr_id = response.headers["x-correlation-id"]
    # Verifica que es un UUID válido
    parsed = uuid.UUID(corr_id)
    assert str(parsed) == corr_id
