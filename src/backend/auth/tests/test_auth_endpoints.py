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
    assert response.json()["message"] == "User registered successfully"
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
    assert response.json()["detail"] == "User already registered"


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
