import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import ASGITransport, AsyncClient

from app.database import get_db
from app.main import app
from travelhub_common.security import RoleEnum, User, get_current_user

USUARIO_ID = uuid.UUID("10000000-0000-4000-8000-000000000001")


@pytest.fixture
def mock_db_session():
    session = AsyncMock()
    session.execute = AsyncMock()
    return session


@pytest.fixture
async def override_manager_client(mock_db_session):
    async def override_get_db():
        yield mock_db_session

    def override_user():
        return User(
            id=uuid.uuid4(),
            email="manager@test.com",
            role=RoleEnum.MANAGER,
        )

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_user

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_usuarios_resumen_returns_200(override_manager_client, mock_db_session):
    viajero = MagicMock()
    viajero.nombre = "Alice Montgomery"

    usuario = MagicMock()
    usuario.id = USUARIO_ID
    usuario.email = "alice@example.com"
    usuario.viajero = viajero

    result = MagicMock()
    scalar_result = MagicMock()
    scalar_result.all.return_value = [usuario]
    result.scalars.return_value = scalar_result
    mock_db_session.execute = AsyncMock(return_value=result)

    response = await override_manager_client.get(
        "/usuarios/resumen",
        params=[("ids", str(USUARIO_ID))],
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data["usuarios"]) == 1
    assert data["usuarios"][0]["id"] == str(USUARIO_ID)
    assert data["usuarios"][0]["nombre"] == "Alice Montgomery"
    assert data["usuarios"][0]["email"] == "alice@example.com"


@pytest.mark.asyncio
async def test_get_usuarios_resumen_401_missing_authorization(mock_db_session):
    async def override_get_db():
        yield mock_db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/usuarios/resumen", params=[("ids", str(USUARIO_ID))])

        assert response.status_code == 401
    finally:
        app.dependency_overrides.clear()
