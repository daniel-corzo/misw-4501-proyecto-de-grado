import pytest
from fastapi import FastAPI, APIRouter
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock
from travelhub_common.factory import create_app


@pytest.mark.anyio
async def test_create_app_returns_fastapi():
    app = create_app("my-service")
    assert isinstance(app, FastAPI)
    assert "my-service" in app.title


@pytest.mark.anyio
async def test_create_app_health_no_db():
    app = create_app("my-service")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "my-service"


@pytest.mark.anyio
async def test_create_app_health_service_prefixed_route():
    app = create_app("my-service")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/my-service/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


@pytest.mark.anyio
async def test_create_app_health_with_db():
    async def mock_get_db():
        mock_session = AsyncMock()
        mock_session.execute = AsyncMock()
        yield mock_session

    app = create_app("db-service", get_db=mock_get_db)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["service"] == "db-service"


@pytest.mark.anyio
async def test_create_app_includes_custom_router():
    router = APIRouter()

    @router.get("/custom")
    async def custom_endpoint():
        return {"custom": True}

    app = create_app("my-service", routers=[router])
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/custom")
    assert response.status_code == 200
    assert response.json() == {"custom": True}


@pytest.mark.anyio
async def test_create_app_cors_headers():
    app = create_app("my-service")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.options(
            "/health",
            headers={"Origin": "http://example.com", "Access-Control-Request-Method": "GET"},
        )
    assert response.status_code in (200, 400)
    assert "access-control-allow-origin" in response.headers
