import uuid
import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app
from app.database import get_db
from unittest.mock import AsyncMock, patch
from travelhub_common.security import RoleEnum, User, get_current_user

class _ScalarResult:
    def __init__(self, value):
        self._value = value

    def scalar_one_or_none(self):
        return self._value

@pytest.fixture
async def mock_db_session():
    from unittest.mock import MagicMock
    session = AsyncMock()
    session.add = MagicMock()
    return session

@pytest.fixture
async def override_client(mock_db_session):
    async def override_get_db():
        yield mock_db_session

    def override_user():
        return User(
            id=uuid.uuid4(),
            email="hotel@test.com",
            role=RoleEnum.MANAGER,
        )

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_user

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_crear_habitacion_endpoint(client: AsyncClient):
    # Unauthenticated request
    hotel_id = uuid.uuid4()
    body = {
        "capacidad": 2,
        "numero": "101",
        "descripcion": "Vista al mar",
        "monto": 100,
        "impuestos": 10
    }
    
    response = await client.post("/hoteles/habitaciones", json=body)
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_crear_habitacion_endpoint_authenticated(override_client, mock_db_session):
    hotel_id = uuid.uuid4()
    body = {
        "capacidad": 2,
        "numero": "101",
        "descripcion": "Vista al mar",
        "monto": 100,
        "impuestos": 10
    }

    mock_db_session.execute = AsyncMock(return_value=_ScalarResult(User(id=hotel_id, email="hotel@test.com", role=RoleEnum.USER)))

    with patch("app.services.habitacion_service.Habitacion", autospec=True) as MockHabitacion:
        mock_instance = MockHabitacion.return_value
        mock_instance.id = uuid.uuid4()
        mock_instance.numero = body["numero"]
        mock_instance.capacidad = body["capacidad"]
        mock_instance.descripcion = body["descripcion"]
        mock_instance.monto = body["monto"]
        mock_instance.impuestos = body["impuestos"]
        mock_instance.disponible = True
        mock_instance.imagenes = []

        response = await override_client.post("/hoteles/habitaciones", json=body)

    assert response.status_code == 201
    data = response.json()
    assert data["capacidad"] == 2
