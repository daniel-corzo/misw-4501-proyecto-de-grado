import os
import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import ASGITransport, AsyncClient

os.environ.setdefault("ENVIRONMENT", "test")

from app.database import get_db
from app.main import app
from travelhub_common.security import RoleEnum, User, get_current_user

USER_ID = uuid.UUID("00000000-0000-4000-8000-000000000001")
HABITACION_ID = uuid.UUID("00000000-0000-4000-8000-000000000002")
OTHER_USER_ID = uuid.UUID("00000000-0000-4000-8000-000000000099")


@pytest.fixture
def mock_db_session():
    session = AsyncMock()
    session.add = MagicMock()

    async def mock_refresh(instance, attribute_names=None):
        if getattr(instance, "created_at", None) is None:
            instance.created_at = datetime.now(UTC)

    session.refresh = AsyncMock(side_effect=mock_refresh)
    session.flush = AsyncMock()
    session.commit = AsyncMock()
    return session


@pytest.fixture
async def override_client(mock_db_session):
    async def override_get_db():
        yield mock_db_session

    def override_user():
        return User(
            id=USER_ID,
            email="viajero@test.com",
            role=RoleEnum.USER,
        )

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_user

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()


def _valid_payload():
    return {
        "usuario_id": str(USER_ID),
        "habitacion_id": str(HABITACION_ID),
        "fecha_entrada": "2026-05-01",
        "fecha_salida": "2026-05-05",
        "num_huespedes": 2,
    }


@pytest.mark.asyncio
async def test_post_reservas_creates_201(override_client, mock_db_session):
    response = await override_client.post("/reservas", json=_valid_payload())

    assert response.status_code == 201
    data = response.json()
    assert data["usuario_id"] == str(USER_ID)
    assert data["habitacion_id"] == str(HABITACION_ID)
    assert data["fecha_entrada"] == "2026-05-01"
    assert data["fecha_salida"] == "2026-05-05"
    assert data["num_huespedes"] == 2
    assert data["estado"] == "pendiente"
    assert data["pago_id"] is None
    assert "id" in data
    assert "created_at" in data
    assert mock_db_session.flush.await_count == 1
    assert mock_db_session.commit.await_count == 1
    assert mock_db_session.refresh.await_count == 1
    mock_db_session.add.assert_called_once()


@pytest.mark.asyncio
async def test_post_reservas_403_other_user(mock_db_session):
    async def override_get_db():
        yield mock_db_session

    def override_user():
        return User(
            id=USER_ID,
            email="viajero@test.com",
            role=RoleEnum.USER,
        )

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_user

    try:
        payload = _valid_payload()
        payload["usuario_id"] = str(OTHER_USER_ID)

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/reservas", json=payload)

        assert response.status_code == 403
        assert response.json()["detail"] == "No tienes permiso para crear una reserva para otro usuario"
        mock_db_session.add.assert_not_called()
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_post_reservas_422_invalid_dates(override_client):
    payload = _valid_payload()
    payload["fecha_salida"] = "2026-05-01"
    payload["fecha_entrada"] = "2026-05-05"

    response = await override_client.post("/reservas", json=payload)

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_post_reservas_401_unauthenticated(mock_db_session):
    async def override_get_db():
        yield mock_db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/reservas", json=_valid_payload())
        assert response.status_code == 401
    finally:
        app.dependency_overrides.clear()
