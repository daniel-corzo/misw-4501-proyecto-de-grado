import uuid
from datetime import time

import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app
from app.database import get_db
from unittest.mock import AsyncMock, patch
from travelhub_common.security import RoleEnum, User, get_current_user
from app.models.habitacion import Habitacion
from app.models.hotel import Hotel

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

    mock_hotel = Hotel(
        id=hotel_id,
        nombre="Hotel Test",
        direccion="Calle 1",
        pais="CO",
        departamento="Cundinamarca",
        ciudad="Bogotá",
        check_in=time(14, 0),
        check_out=time(11, 0),
        usuario_id=uuid.uuid4(),
    )
    mock_db_session.execute = AsyncMock(
        return_value=_ScalarResult(mock_hotel)
    )

    response = await override_client.post("/hoteles/habitaciones", json=body)

    assert response.status_code == 201
    data = response.json()
    assert data["capacidad"] == 2


@pytest.mark.asyncio
async def test_actualizar_habitacion_endpoint(client: AsyncClient):
    room_id = uuid.uuid4()
    body = {
        "capacidad": 3,
        "numero": "202",
        "descripcion": "Suite remodelada",
        "monto": 200,
        "impuestos": 20,
    }

    response = await client.put(f"/hoteles/habitaciones/{room_id}", json=body)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_actualizar_habitacion_endpoint_authenticated(override_client, mock_db_session):
    hotel_id = uuid.uuid4()
    room_id = uuid.uuid4()
    body = {
        "capacidad": 3,
        "numero": "202",
        "descripcion": "Suite remodelada",
        "monto": 200,
        "impuestos": 20,
        "imagenes": ["https://example.com/habitacion.jpg"],
    }

    mock_hotel = Hotel(
        id=hotel_id,
        nombre="Hotel Test",
        direccion="Calle 1",
        pais="CO",
        departamento="Cundinamarca",
        ciudad="Bogotá",
        check_in=time(14, 0),
        check_out=time(11, 0),
        usuario_id=uuid.uuid4(),
    )
    existing_room = Habitacion(
        id=room_id,
        capacidad=2,
        numero="101",
        descripcion="Vista al mar",
        monto=100,
        impuestos=10,
        disponible=False,
        imagenes=[],
        hotel_id=hotel_id,
    )
    mock_db_session.execute = AsyncMock(
        side_effect=[
            _ScalarResult(mock_hotel),
            _ScalarResult(existing_room),
            _ScalarResult(None),
        ]
    )

    response = await override_client.put(
        f"/hoteles/habitaciones/{room_id}",
        json=body,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(room_id)
    assert data["capacidad"] == 3
    assert data["numero"] == "202"
    assert data["descripcion"] == "Suite remodelada"
    assert data["monto"] == 200
    assert data["impuestos"] == 20
    assert data["imagenes"] == ["https://example.com/habitacion.jpg"]
    assert data["disponible"] is True

@pytest.mark.asyncio
async def test_listar_habitaciones_endpoint_authenticated(override_client, mock_db_session):
    hotel_id = uuid.uuid4()
    mock_db_session.execute = AsyncMock(return_value=_ScalarResult(User(id=hotel_id, email="hotel@test.com", role=RoleEnum.USER)))

    with patch("app.routers.hoteles.listar_habitaciones_service", autospec=True) as MockListarService:
        from app.schemas.hotel import ListaHabitacionesResponse, HabitacionDetalleResponse
        mock_response = ListaHabitacionesResponse(
            total=1,
            habitaciones=[
                HabitacionDetalleResponse(
                    id=uuid.uuid4(),
                    capacidad=2,
                    numero="101",
                    descripcion="Vista al mar",
                    monto=100,
                    impuestos=10,
                    disponible=True,
                    imagenes=[]
                )
            ]
        )
        MockListarService.return_value = mock_response

        response = await override_client.get("/hoteles/habitaciones?limit=10&offset=0")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert len(data["habitaciones"]) == 1
    assert data["habitaciones"][0]["numero"] == "101"
