import datetime
import os
import pytest
import uuid
from unittest.mock import AsyncMock, patch, MagicMock
from httpx import AsyncClient, ASGITransport, Response, Request, HTTPStatusError, RequestError

from app.models.usuario import TipoUsuario

os.environ.setdefault("ENVIRONMENT", "test")

from app.main import app
from app.database import get_db
from travelhub_common.security import RoleEnum

VALID_PAYLOAD = {
    "email": "test@example.com",
    "password": "strongPassword123",
    "nombre": "Test",
    "telefono": "1234567890",
    "tipo": TipoUsuario.VIAJERO.value,
    "role": RoleEnum.USER.value,
}

@pytest.fixture
def mock_db_session():
    mock_session = AsyncMock()
    mock_session.add = MagicMock()
    
    # Configure the execute().scalars().first() chain to return None.
    # This avoids triggering the duplicate profile id check by default.
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = None
    mock_session.execute.return_value = mock_result
    
    async def mock_refresh(instance):
        instance.created_at = datetime.datetime.now(datetime.UTC).isoformat()
    mock_session.refresh.side_effect = mock_refresh
    
    return mock_session

@pytest.fixture
async def override_client(mock_db_session):
    async def override_get_db():
        yield mock_db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as c:
        yield c

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_register_viajero_success(override_client, mock_db_session):
    # Execute POST
    response = await override_client.post("/usuarios", json=VALID_PAYLOAD)

    assert response.status_code == 201
    data = response.json()

    assert data["id"] is not None
    assert data["email"] == VALID_PAYLOAD["email"]
    assert data["tipo"] == VALID_PAYLOAD["tipo"]
    assert data["viajero"] is not None
    assert data["viajero"]["id"] is not None
    assert data["viajero"]["nombre"] == VALID_PAYLOAD["nombre"]
    assert data["viajero"]["contacto"] == VALID_PAYLOAD["telefono"]


@pytest.mark.asyncio
async def test_register_id_already_exists(override_client, mock_db_session):
    # Adjust mock to simulate an existing user profile with duplicated id
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = MagicMock()
    mock_db_session.execute.return_value = mock_result

    response = await override_client.post("/usuarios", json=VALID_PAYLOAD)

    assert response.status_code == 400
    assert response.json()["detail"] == "Usuario ya existe con este email"

    # Remote call completely stalled and records weren't touched
    mock_db_session.add.assert_not_called()


# TODO: Could be used for hotels call
# @pytest.mark.asyncio
# async def test_register_auth_service_http_error(override_client, mock_db_session):
#     with patch("app.services.usuario_service.httpx.AsyncClient") as MockClient:
#         mock_client_instance = MockClient.return_value.__aenter__.return_value

#         # Mock HTTP Error natively returned from Auth MS (Fail state code)
#         error_response = Response(status_code=400, json={"detail": "Password too weak"})
#         request = Request("POST", "http://auth:8000/auth/register")
#         error = HTTPStatusError("Error", request=request, response=error_response)

#         mock_client_instance.post.side_effect = error

#         response = await override_client.post("/usuarios", json=VALID_PAYLOAD)

#         assert response.status_code == 400
#         assert response.json()["detail"] == "Password too weak"

#         # Verified DB rollback
#         assert mock_db_session.rollback.called
#         assert not mock_db_session.commit.called

# TODO: Could be used for hotels call
# @pytest.mark.asyncio
# async def test_register_auth_service_unavailable(override_client, mock_db_session):
#     with patch("app.services.usuario_service.httpx.AsyncClient") as MockClient:
#         mock_client_instance = MockClient.return_value.__aenter__.return_value

#         # Mock Auth MS not responding
#         request = Request("POST", "http://auth:8000/auth/register")
#         error = RequestError("Connection Refused", request=request)

#         mock_client_instance.post.side_effect = error

#         response = await override_client.post("/usuarios", json=VALID_PAYLOAD)

#         assert response.status_code == 503
#         assert response.json()["detail"] == "Auth MS no esta disponible"

#         # Verified DB rollback
#         assert mock_db_session.rollback.called
#         assert not mock_db_session.commit.called
