import uuid
from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

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
@patch("app.services.hotel_service.httpx.AsyncClient")
async def test_post_hoteles_creates_with_politicas_and_habitaciones(mock_async_client, override_client, mock_db_session):
    mock_response = MagicMock()
    mock_response.status_code = 201
    mock_response.json.return_value = {"id": str(uuid.uuid4())}
    mock_client_instance = AsyncMock()
    mock_client_instance.post.return_value = mock_response
    mock_client_instance.__aenter__.return_value = mock_client_instance
    mock_async_client.return_value = mock_client_instance

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
        numero="101",
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
        amenidades=["WIFI", "POOL"],
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
        "amenidades": ["WIFI", "POOL"],
        "estrellas": 5,
        "ranking": 4.8,
        "contacto_celular": "3000000000",
        "contacto_email": "hotel@nuevo.com",
        "email": "hotel@nuevo.com",
        "password": "secretpassword",
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
                "numero": "101",
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
@patch("app.services.hotel_service.httpx.AsyncClient")
async def test_post_hoteles_creates_without_optional_lists(mock_async_client, override_client, mock_db_session):
    mock_response = MagicMock()
    mock_response.status_code = 201
    mock_response.json.return_value = {"id": str(uuid.uuid4())}
    mock_client_instance = AsyncMock()
    mock_client_instance.post.return_value = mock_response
    mock_client_instance.__aenter__.return_value = mock_client_instance
    mock_async_client.return_value = mock_client_instance

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
        amenidades=["WIFI"],
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
        "amenidades": ["WIFI"],
        "estrellas": 4,
        "ranking": 4.2,
        "imagenes": [],
        "email": "hotel@nuevo.com",
        "password": "secretpassword",
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
        amenidades=[],
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
        numero="201",
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
        amenidades=["WIFI", "POOL"],
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


@pytest.mark.asyncio
async def test_get_hotel_detalle_returns_401_when_unauthenticated(mock_db_session):
    """GET /hoteles/{id} without auth → 401."""
    async def override_get_db():
        yield mock_db_session

    app.dependency_overrides[get_db] = override_get_db
    # intentionally NOT overriding get_current_user so the real JWT check runs

    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(f"/hoteles/{uuid.uuid4()}")
        assert response.status_code == 401
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_hotel_detalle_returns_hotel_without_rooms_and_politicas(override_client, mock_db_session):
    """Edge case: hotel with empty habitaciones and politicas lists."""
    hotel_id = uuid.uuid4()
    usuario_id = uuid.uuid4()
    hotel = SimpleNamespace(
        id=hotel_id,
        nombre="Hotel Mínimo",
        direccion="Calle 5",
        pais="Colombia",
        estado=None,
        departamento="Cundinamarca",
        ciudad="Bogota",
        descripcion=None,
        amenidades=[],
        estrellas=3,
        ranking=4.0,
        contacto_celular=None,
        contacto_email=None,
        imagenes=[],
        check_in=datetime.now(UTC).time(),
        check_out=datetime.now(UTC).time(),
        valor_minimo_modificacion=50.0,
        usuario_id=usuario_id,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
        politicas=[],
        habitaciones=[],
    )

    mock_db_session.execute = AsyncMock(return_value=_ScalarResult(hotel))

    response = await override_client.get(f"/hoteles/{hotel_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(hotel_id)
    assert data["politicas"] == []
    assert data["habitaciones"] == []
    assert data["amenidades"] == []
    assert data["imagenes"] == []


@pytest.mark.asyncio
async def test_get_hoteles_filters_by_ciudad(override_client, mock_db_session):
    hotel = SimpleNamespace(
        id=uuid.uuid4(),
        nombre="Hotel Bogota",
        ciudad="Bogota",
        pais="Colombia",
        estrellas=4,
        amenidades=[],
        imagenes=[],
        created_at=datetime.now(UTC),
    )

    mock_db_session.execute = AsyncMock(
        side_effect=[
            _ScalarResult(1),
            _RowsResult([(hotel, 200)]),
        ]
    )

    response = await override_client.get("/hoteles?ciudad=Bogo")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["hoteles"][0]["ciudad"] == "Bogota"


@pytest.mark.asyncio
async def test_get_hoteles_filters_by_capacidad_min(override_client, mock_db_session):
    hotel = SimpleNamespace(
        id=uuid.uuid4(),
        nombre="Hotel Familiar",
        ciudad="Medellin",
        pais="Colombia",
        estrellas=3,
        amenidades=[],
        imagenes=[],
        created_at=datetime.now(UTC),
    )

    mock_db_session.execute = AsyncMock(
        side_effect=[
            _ScalarResult(1),
            _RowsResult([(hotel, 450)]),
        ]
    )

    response = await override_client.get("/hoteles?capacidad_min=4")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["hoteles"][0]["nombre"] == "Hotel Familiar"


@pytest.mark.asyncio
async def test_get_hoteles_orden_nombre_asc(override_client, mock_db_session):
    hotel = SimpleNamespace(
        id=uuid.uuid4(),
        nombre="Andino Royal",
        ciudad="Bogota",
        pais="Colombia",
        estrellas=5,
        amenidades=[],
        imagenes=[],
        created_at=datetime.now(UTC),
    )

    mock_db_session.execute = AsyncMock(
        side_effect=[
            _ScalarResult(1),
            _RowsResult([(hotel, 300)]),
        ]
    )

    response = await override_client.get("/hoteles?orden=nombre_asc")

    assert response.status_code == 200
    data = response.json()
    assert data["hoteles"][0]["nombre"] == "Andino Royal"


@pytest.mark.asyncio
async def test_get_hoteles_orden_nombre_desc(override_client, mock_db_session):
    hotel = SimpleNamespace(
        id=uuid.uuid4(),
        nombre="Zona Rosa Hotel",
        ciudad="Bogota",
        pais="Colombia",
        estrellas=4,
        amenidades=[],
        imagenes=[],
        created_at=datetime.now(UTC),
    )

    mock_db_session.execute = AsyncMock(
        side_effect=[
            _ScalarResult(1),
            _RowsResult([(hotel, 250)]),
        ]
    )

    response = await override_client.get("/hoteles?orden=nombre_desc")

    assert response.status_code == 200
    data = response.json()
    assert data["hoteles"][0]["nombre"] == "Zona Rosa Hotel"


@pytest.mark.asyncio
async def test_get_hoteles_returns_422_for_invalid_capacidad_min(override_client, mock_db_session):
    response = await override_client.get("/hoteles?capacidad_min=0")
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_hotel_detalle_response_has_all_expected_fields(override_client, mock_db_session):
    """Assert all top-level fields are present in the response."""
    hotel_id = uuid.uuid4()
    usuario_id = uuid.uuid4()
    hotel = SimpleNamespace(
        id=hotel_id,
        nombre="Hotel Completo",
        direccion="Av. 123",
        pais="Colombia",
        estado="Cundinamarca",
        departamento="Cundinamarca",
        ciudad="Bogota",
        descripcion="Descripcion completa",
        amenidades=["WIFI", "POOL"],
        estrellas=5,
        ranking=4.9,
        contacto_celular="3001234567",
        contacto_email="completo@hotel.com",
        imagenes=["img1.jpg", "img2.jpg"],
        check_in=datetime.now(UTC).time(),
        check_out=datetime.now(UTC).time(),
        valor_minimo_modificacion=120.0,
        usuario_id=usuario_id,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
        politicas=[],
        habitaciones=[],
    )

    mock_db_session.execute = AsyncMock(return_value=_ScalarResult(hotel))

    response = await override_client.get(f"/hoteles/{hotel_id}")

    assert response.status_code == 200
    data = response.json()

    expected_fields = [
        "id", "nombre", "direccion", "estado", "pais", "departamento", "ciudad",
        "descripcion", "amenidades", "estrellas", "ranking",
        "contacto_celular", "contacto_email", "imagenes",
        "check_in", "check_out", "valor_minimo_modificacion",
        "usuario_id", "created_at", "updated_at", "politicas", "habitaciones",
    ]
    for field in expected_fields:
        assert field in data, f"Missing field: {field}"

    assert data["nombre"] == "Hotel Completo"
    assert data["estrellas"] == 5
    assert data["ranking"] == 4.9
    assert data["imagenes"] == ["img1.jpg", "img2.jpg"]


# ── DELETE /hoteles/habitaciones/{habitacion_id} ─────────────────────────────

@pytest.mark.asyncio
async def test_delete_habitacion_returns_204_when_owner_deletes(override_client, mock_db_session):
    user_id = uuid.uuid4()
    hotel_id = uuid.uuid4()
    habitacion_id = uuid.uuid4()

    def override_user():
        return User(id=user_id, email="hotel@test.com", role=RoleEnum.USER)

    app.dependency_overrides[get_current_user] = override_user

    habitacion = SimpleNamespace(id=habitacion_id, hotel_id=hotel_id)
    hotel = SimpleNamespace(id=hotel_id, usuario_id=user_id)

    execute_results = [_ScalarResult(habitacion), _ScalarResult(hotel)]
    call_count = 0

    async def multi_execute(stmt, *args, **kwargs):
        nonlocal call_count
        result = execute_results[min(call_count, len(execute_results) - 1)]
        call_count += 1
        return result

    mock_db_session.execute = multi_execute
    mock_db_session.delete = AsyncMock()

    response = await override_client.delete(f"/hoteles/habitaciones/{habitacion_id}")

    assert response.status_code == 204
    assert mock_db_session.commit.await_count >= 1


@pytest.mark.asyncio
async def test_delete_habitacion_returns_403_when_not_owner(override_client, mock_db_session):
    requester_id = uuid.uuid4()
    owner_id = uuid.uuid4()
    hotel_id = uuid.uuid4()
    habitacion_id = uuid.uuid4()

    def override_user():
        return User(id=requester_id, email="otro@test.com", role=RoleEnum.USER)

    app.dependency_overrides[get_current_user] = override_user

    habitacion = SimpleNamespace(id=habitacion_id, hotel_id=hotel_id)
    hotel_ajeno = SimpleNamespace(id=uuid.uuid4(), usuario_id=owner_id)

    execute_results = [_ScalarResult(habitacion), _ScalarResult(hotel_ajeno)]
    call_count = 0

    async def multi_execute(stmt, *args, **kwargs):
        nonlocal call_count
        result = execute_results[min(call_count, len(execute_results) - 1)]
        call_count += 1
        return result

    mock_db_session.execute = multi_execute

    response = await override_client.delete(f"/hoteles/habitaciones/{habitacion_id}")

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_delete_habitacion_returns_204_when_admin_deletes_any(override_client, mock_db_session):
    admin_id = uuid.uuid4()
    habitacion_id = uuid.uuid4()

    def override_admin():
        return User(id=admin_id, email="admin@test.com", role=RoleEnum.ADMIN)

    app.dependency_overrides[get_current_user] = override_admin

    habitacion = SimpleNamespace(id=habitacion_id, hotel_id=uuid.uuid4())
    mock_db_session.execute = AsyncMock(return_value=_ScalarResult(habitacion))
    mock_db_session.delete = AsyncMock()

    response = await override_client.delete(f"/hoteles/habitaciones/{habitacion_id}")

    assert response.status_code == 204


@pytest.mark.asyncio
async def test_delete_habitacion_returns_404_when_not_found(override_client, mock_db_session):
    mock_db_session.execute = AsyncMock(return_value=_ScalarResult(None))

    response = await override_client.delete(f"/hoteles/habitaciones/{uuid.uuid4()}")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_habitacion_returns_401_when_unauthenticated(mock_db_session):
    async def override_get_db():
        yield mock_db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.delete(f"/hoteles/habitaciones/{uuid.uuid4()}")
        assert response.status_code == 401
    finally:
        app.dependency_overrides.clear()
