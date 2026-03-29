import pytest
from uuid import uuid4
from unittest.mock import AsyncMock, patch, MagicMock
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.database import get_db
from app.models.user import UserCredentials
from travelhub_common.security import RoleEnum
from app.routers.auth import get_settings
from travelhub_common.config import BaseAppSettings

@pytest.fixture
def mock_db_session():
    mock_session = AsyncMock()
    return mock_session

@pytest.fixture
async def override_client(mock_db_session):
    async def override_get_db():
        yield mock_db_session

    app.dependency_overrides[get_db] = override_get_db
    
    # We must patch get_settings explicitly because create_access_token uses the RSA logic 
    # and would otherwise crash looking for a real loaded pair without mock!
    test_settings = BaseAppSettings(
        jwt_private_key="test_key", 
        jwt_algorithm="HS256", 
        jwt_secret="local-secret"
    )
    app.dependency_overrides[get_settings] = lambda: test_settings

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as c:
        yield c

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_register_success(override_client, mock_db_session):
    """Test successful user registration creates ID and checks duplicate properly"""
    # Simulate SELECT ... => None (no user exists)
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = None
    mock_db_session.execute.return_value = mock_result

    response = await override_client.post("/auth/register", json={
        "email": "unique@example.com",
        "password": "securepassword123*",
        "role": "USER"  # Using string mapping logic matching payload payload default enum bounds
    })

    assert response.status_code == 201
    assert response.json()["message"] == "Usuario registrado correctamente"
    assert "id" in response.json()
    assert mock_db_session.add.called
    assert mock_db_session.commit.called


@pytest.mark.asyncio
async def test_register_duplicate_email(override_client, mock_db_session):
    """Test register crashes on duplicate emails natively via HTTP 400"""
    # Simulate SELECT ... => Returing a valid object breaking the constraint
    mock_result = MagicMock()
    dummy_user = UserCredentials(id=uuid4(), email="duplicate@example.com")
    mock_result.scalars.return_value.first.return_value = dummy_user
    mock_db_session.execute.return_value = mock_result

    response = await override_client.post("/auth/register", json={
        "email": "duplicate@example.com",
        "password": "pass",
    })

    assert response.status_code == 400
    assert response.json()["detail"] == "El correo ya esta registrado"


@pytest.mark.asyncio
async def test_login_success(override_client, mock_db_session):
    """Test login issues a token properly bypassing Pydantic validations"""
    # Provide a hash corresponding to "password123" matching verify_password criteria
    from app.services.auth_service import get_password_hash
    hashed = get_password_hash("password123")
    
    mock_result = MagicMock()
    valid_user = UserCredentials(
        id=uuid4(),
        email="login@example.com",
        hashed_password=hashed,
        role=RoleEnum.USER
    )
    mock_result.scalars.return_value.first.return_value = valid_user
    mock_db_session.execute.return_value = mock_result

    response = await override_client.post("/auth/login", json={
        "email": "login@example.com",
        "password": "password123"
    })

    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_invalid_password(override_client, mock_db_session):
    """Test login rejects invalid signatures on existing credentials"""
    from app.services.auth_service import get_password_hash
    hashed = get_password_hash("password123")

    mock_result = MagicMock()
    valid_user = UserCredentials(
        id=uuid4(),
        email="login@example.com",
        hashed_password=hashed,
        role=RoleEnum.USER
    )
    mock_result.scalars.return_value.first.return_value = valid_user
    mock_db_session.execute.return_value = mock_result

    response = await override_client.post("/auth/login", json={
        "email": "login@example.com",
        "password": "WRONG_password123"
    })

    assert response.status_code == 401
    assert response.json()["detail"] == "Credenciales invalidas"


# ── Logout ────────────────────────────────────────────────────────────────────

SYMMETRIC_KEY = "test_key_for_logout"

@pytest.fixture
async def logout_client(mock_db_session):
    """Client fixture con configuracion simetrica para tests de logout."""
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

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c, test_settings

    app.dependency_overrides.clear()


def _make_test_token(settings: BaseAppSettings) -> str:
    from app.services.auth_service import create_access_token
    return create_access_token(
        {"sub": str(uuid4()), "email": "test@test.com", "role": "USER"},
        settings,
    )


@pytest.mark.asyncio
async def test_logout_success(logout_client, mock_db_session):
    """Logout con token valido retorna 200 y persiste la revocacion."""
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
    """Logout con token invalido retorna 401."""
    client, _ = logout_client

    response = await client.post(
        "/auth/logout",
        headers={"Authorization": "Bearer esto.no.es.un.jwt"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Token invalido"


@pytest.mark.asyncio
async def test_logout_no_token(logout_client):
    """Logout sin header Authorization retorna 403."""
    client, _ = logout_client

    response = await client.post("/auth/logout")

    assert response.status_code == 403
