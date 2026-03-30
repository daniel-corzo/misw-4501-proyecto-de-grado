import pytest
from httpx import ASGITransport, AsyncClient
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from app.config import get_settings
from app.database import get_db
from app.main import app
from app.models.usuario import TipoUsuario, Usuario
from app.services.auth_service import create_access_token, get_password_hash
from travelhub_common.config import BaseAppSettings
from travelhub_common.security import RoleEnum


@pytest.fixture
def mock_db_session():
    mock_session = AsyncMock()
    return mock_session


@pytest.fixture
async def override_client(mock_db_session):
    async def override_get_db():
        yield mock_db_session

    app.dependency_overrides[get_db] = override_get_db

    test_settings = BaseAppSettings(
        jwt_private_key="test_key",
        jwt_algorithm="HS256",
        jwt_secret="local-secret",
    )
    app.dependency_overrides[get_settings] = lambda: test_settings

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as c:
        yield c

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_login_success(override_client, mock_db_session):
    hashed = get_password_hash("password123")

    mock_result = MagicMock()
    valid_user = Usuario(
        id=uuid4(),
        email="login@example.com",
        hashed_contrasena=hashed,
        tipo=TipoUsuario.VIAJERO,
        role=RoleEnum.USER,
    )
    mock_result.scalars.return_value.first.return_value = valid_user
    mock_db_session.execute.return_value = mock_result

    response = await override_client.post(
        "/auth/login",
        json={
            "email": "login@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_invalid_password(override_client, mock_db_session):
    hashed = get_password_hash("password123")

    mock_result = MagicMock()
    valid_user = Usuario(
        id=uuid4(),
        email="login@example.com",
        hashed_contrasena=hashed,
        tipo=TipoUsuario.VIAJERO,
        role=RoleEnum.USER,
    )
    mock_result.scalars.return_value.first.return_value = valid_user
    mock_db_session.execute.return_value = mock_result

    response = await override_client.post(
        "/auth/login",
        json={
            "email": "login@example.com",
            "password": "WRONG_password123",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Credenciales invalidas"


SYMMETRIC_KEY = "test_key_for_logout"


@pytest.fixture
async def logout_client(mock_db_session):
    async def override_get_db():
        yield mock_db_session

    test_settings = BaseAppSettings(
        jwt_private_key=SYMMETRIC_KEY,
        jwt_public_key=SYMMETRIC_KEY,
        jwt_algorithm="HS256",
        jwt_secret="local-secret",
    )
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_settings] = lambda: test_settings

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as c:
        yield c, test_settings

    app.dependency_overrides.clear()


def _make_test_token(settings: BaseAppSettings) -> str:
    return create_access_token(
        {"sub": str(uuid4()), "email": "test@test.com", "role": "USER"},
        settings,
    )


@pytest.mark.asyncio
async def test_logout_success(logout_client, mock_db_session):
    client, settings = logout_client
    token = _make_test_token(settings)

    response = await client.post(
        "/auth/logout",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Sesion cerrada correctamente"
    assert mock_db_session.add.called
    assert mock_db_session.commit.called


@pytest.mark.asyncio
async def test_logout_invalid_token(logout_client):
    client, _ = logout_client

    response = await client.post(
        "/auth/logout",
        headers={"Authorization": "Bearer esto.no.es.un.jwt"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Token invalido"


@pytest.mark.asyncio
async def test_logout_no_token(logout_client):
    client, _ = logout_client

    response = await client.post("/auth/logout")

    assert response.status_code == 401
