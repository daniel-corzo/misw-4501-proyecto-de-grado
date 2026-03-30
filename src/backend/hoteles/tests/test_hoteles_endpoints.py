import uuid
from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import ASGITransport, AsyncClient

from app.database import get_db
from app.main import app
from travelhub_common.security import RoleEnum, User, get_current_user


class _ScalarResult:
    def __init__(self, value):
        self._value = value

    def scalar_one(self):
        return self._value

    def scalar_one_or_none(self):
        return self._value


class _RowsResult:
    def __init__(self, rows):
        self._rows = rows

    def all(self):
        return self._rows


@pytest.fixture
def mock_db_session():
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
            email="manager@test.com",
            role=RoleEnum.MANAGER,
        )

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_user

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_post_hoteles_creates_with_politicas_and_habitaciones(override_client, mock_db_session):
    hotel_id = uuid.uuid4()
    usuario_id = uuid.uuid4()
    created_at = datetime.now(UTC)
    updated_at = datetime.now(UTC)

    politica = SimpleNamespace(
        id=uuid.uuid4(),
        nombre="Cancelacion flexible",
        descripcion="Gratis hasta 24h",
        tipo="cancelacion",
        penalizacion=0,
        dias_antelacion=1,
    )
    habitacion = SimpleNamespace(
        id=uuid.uuid4(),
        capacidad=2,
        numero=101,
        descripcion="Vista ciudad",
        imagenes=["h1.jpg"],
        monto=250,
        impuestos=45,
        disponible=True,
    )
    hotel = SimpleNamespace(
        id=hotel_id,
        nombre="Hotel Nuevo",
        direccion="Calle 10",
        pais="Colombia",
        estado="Cundinamarca",
        departamento="Cundinamarca",
        ciudad="Medellin",
        descripcion="Hotel de prueba",
        amenidades=["Wi-Fi", "Pool"],
        estrellas=5,
        ranking=4.8,
        contacto_celular="3000000000",
        contacto_email="hotel@nuevo.com",
        imagenes=["hotel1.jpg"],
        check_in=datetime.now(UTC).time(),
        check_out=datetime.now(UTC).time(),
        valor_minimo_modificacion=100.0,
        usuario_id=usuario_id,
        created_at=created_at,
        updated_at=updated_at,
        politicas=[politica],
        habitaciones=[habitacion],
    )

    mock_db_session.execute = AsyncMock(return_value=_ScalarResult(hotel))

    payload = {
        "nombre": "Hotel Nuevo",
        "direccion": "Calle 10",
        "pais": "Colombia",
        "estado": "Cundinamarca",
        "departamento": "Cundinamarca",
        "ciudad": "Medellin",
        "descripcion": "Hotel de prueba",
        "amenidades": ["Wi-Fi", "Pool"],
        "estrellas": 5,
        "ranking": 4.8,
        "contacto_celular": "3000000000",
        "contacto_email": "hotel@nuevo.com",
        "imagenes": ["hotel1.jpg"],
        "check_in": "15:00:00",
        "check_out": "12:00:00",
        "valor_minimo_modificacion": 100.0,
        "usuario_id": str(usuario_id),
        "politicas": [
            {
                "nombre": "Cancelacion flexible",
                "descripcion": "Gratis hasta 24h",
                "tipo": "cancelacion",
                "penalizacion": 0,
                "dias_antelacion": 1,
            }
        ],
        "habitaciones": [
            {
                "capacidad": 2,
                "numero": 101,
                "descripcion": "Vista ciudad",
                "imagenes": ["h1.jpg"],
                "monto": 250,
                "impuestos": 45,
                "disponible": True,
            }
        ],
    }

    response = await override_client.post("/hoteles", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["nombre"] == "Hotel Nuevo"
    assert data["pais"] == "Colombia"
    assert len(data["politicas"]) == 1
    assert len(data["habitaciones"]) == 1
    assert mock_db_session.flush.await_count == 1
    assert mock_db_session.commit.await_count == 1


@pytest.mark.asyncio
async def test_post_hoteles_creates_without_optional_lists(override_client, mock_db_session):
    hotel_id = uuid.uuid4()
    usuario_id = uuid.uuid4()
    created_at = datetime.now(UTC)
    updated_at = datetime.now(UTC)

    hotel = SimpleNamespace(
        id=hotel_id,
        nombre="Hotel Simple",
        direccion="Calle 20",
        pais="Colombia",
        estado="Antioquia",
        departamento="Antioquia",
        ciudad="Medellin",
        descripcion="Solo hotel",
        amenidades=["Wi-Fi"],
        estrellas=4,
        ranking=4.2,
        contacto_celular=None,
        contacto_email=None,
        imagenes=[],
        check_in=datetime.now(UTC).time(),
        check_out=datetime.now(UTC).time(),
        valor_minimo_modificacion=50.0,
        usuario_id=usuario_id,
        created_at=created_at,
        updated_at=updated_at,
        politicas=[],
        habitaciones=[],
    )

    mock_db_session.execute = AsyncMock(return_value=_ScalarResult(hotel))

    payload = {
        "nombre": "Hotel Simple",
        "direccion": "Calle 20",
        "pais": "Colombia",
        "estado": "Antioquia",
        "departamento": "Antioquia",
        "ciudad": "Medellin",
        "descripcion": "Solo hotel",
        "amenidades": ["Wi-Fi"],
        "estrellas": 4,
        "ranking": 4.2,
        "imagenes": [],
        "check_in": "15:00:00",
        "check_out": "12:00:00",
        "valor_minimo_modificacion": 50.0,
        "usuario_id": str(usuario_id),
    }

    response = await override_client.post("/hoteles", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["nombre"] == "Hotel Simple"
    assert data["politicas"] == []
    assert data["habitaciones"] == []
    assert mock_db_session.flush.await_count == 1
    assert mock_db_session.commit.await_count == 1


@pytest.mark.asyncio
async def test_get_hoteles_returns_list_with_imagenes_and_precio_minimo(override_client, mock_db_session):
    hotel = SimpleNamespace(
        id=uuid.uuid4(),
        nombre="Hotel Lista",
        ciudad="Bogota",
        pais="Colombia",
        estrellas=4,
        imagenes=["hotel-lista.jpg"],
        created_at=datetime.now(UTC),
    )

    mock_db_session.execute = AsyncMock(
        side_effect=[
            _ScalarResult(1),
            _RowsResult([(hotel, 180)]),
        ]
    )

    response = await override_client.get("/hoteles")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert len(data["hoteles"]) == 1
    assert data["hoteles"][0]["nombre"] == "Hotel Lista"
    assert data["hoteles"][0]["imagenes"] == ["hotel-lista.jpg"]
    assert data["hoteles"][0]["precio_minimo"] == 180


@pytest.mark.asyncio
async def test_get_hotel_detalle_returns_hotel_with_politicas_and_habitaciones(override_client, mock_db_session):
    hotel_id = uuid.uuid4()
    usuario_id = uuid.uuid4()
    politica = SimpleNamespace(
        id=uuid.uuid4(),
        nombre="No fumadores",
        descripcion="No se permite fumar",
        tipo="convivencia",
        penalizacion=0,
        dias_antelacion=0,
    )
    habitacion = SimpleNamespace(
        id=uuid.uuid4(),
        capacidad=2,
        numero=201,
        descripcion="Suite",
        imagenes=["suite.jpg"],
        monto=500,
        impuestos=95,
        disponible=True,
    )
    hotel = SimpleNamespace(
        id=hotel_id,
        nombre="Hotel Detalle",
        direccion="Cra 1 # 1-1",
        pais="Colombia",
        estado="Cundinamarca",
        departamento="Cundinamarca",
        ciudad="Bogota",
        descripcion="Detalle completo",
        amenidades=["Wi-Fi", "Pool"],
        estrellas=5,
        ranking=4.9,
        contacto_celular="3001234567",
        contacto_email="detalle@hotel.com",
        imagenes=["detalle.jpg"],
        check_in=datetime.now(UTC).time(),
        check_out=datetime.now(UTC).time(),
        valor_minimo_modificacion=120.0,
        usuario_id=usuario_id,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
        politicas=[politica],
        habitaciones=[habitacion],
    )

    mock_db_session.execute = AsyncMock(return_value=_ScalarResult(hotel))

    response = await override_client.get(f"/hoteles/{hotel_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(hotel_id)
    assert data["nombre"] == "Hotel Detalle"
    assert len(data["politicas"]) == 1
    assert len(data["habitaciones"]) == 1
    assert data["habitaciones"][0]["monto"] == 500


@pytest.mark.asyncio
async def test_get_hotel_detalle_returns_404_when_not_found(override_client, mock_db_session):
    mock_db_session.execute = AsyncMock(return_value=_ScalarResult(None))

    response = await override_client.get(f"/hoteles/{uuid.uuid4()}")

    assert response.status_code == 404
    data = response.json()
    assert data["error"] == "not_found"
    assert data["message"] == "El recurso solicitado no existe"