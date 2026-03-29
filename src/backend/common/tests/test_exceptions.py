import pytest
from httpx import AsyncClient, ASGITransport
from fastapi import APIRouter
from pydantic import BaseModel as PydanticModel
from travelhub_common.factory import create_app


@pytest.fixture
def app():
    return create_app("test-service")


@pytest.mark.anyio
async def test_404_handler_returns_json(app):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/route-that-does-not-exist")
    assert response.status_code == 404
    data = response.json()
    assert data["error"] == "not_found"
    assert "correlation_id" in data


@pytest.mark.anyio
async def test_422_handler_returns_json():
    class Body(PydanticModel):
        name: str
        age: int

    router = APIRouter()

    @router.post("/items")
    async def create_item(body: Body):
        return body

    app = create_app("test-service", routers=[router])
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/items", json={"name": "test"})  # falta age
    assert response.status_code == 422
    data = response.json()
    assert data["error"] == "validation_error"
    assert "correlation_id" in data
