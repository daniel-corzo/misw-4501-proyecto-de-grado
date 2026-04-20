import uuid
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock
from unittest.mock import patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.database import get_db
from app.main import app
from app.schemas.reserva import HabitacionHotelResponse, HabitacionReservaDetalleResponse
from travelhub_common.security import RoleEnum, User, get_current_user
from app.models.reserva import Reserva

USER_ID = uuid.UUID("00000000-0000-4000-8000-000000000001")
HABITACION_ID = uuid.UUID("00000000-0000-4000-8000-000000000002")


def _execute_result_no_conflict():
    r = MagicMock()
    r.scalar_one_or_none.return_value = None
    return r


def _execute_result_with_reserva(reserva: Reserva):
    r = MagicMock()
    r.scalar_one_or_none.return_value = reserva
    return r


@pytest.fixture
def mock_db_session():
    session = AsyncMock()
    session.add = MagicMock()
    session.execute = AsyncMock(return_value=_execute_result_no_conflict())

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
    assert mock_db_session.execute.await_count == 1


@pytest.mark.asyncio
async def test_post_reservas_409_overlap(mock_db_session):
    conflict_result = MagicMock()
    conflict_result.scalar_one_or_none.return_value = uuid.uuid4()
    mock_db_session.execute = AsyncMock(return_value=conflict_result)

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
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/reservas", json=_valid_payload())
        assert response.status_code == 409
        assert "habitación" in response.json()["detail"].lower()
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
async def test_post_reservas_401_missing_authorization(mock_db_session):
    """No Authorization header: FastAPI HTTPBearer raises HTTPException with 401 (see HTTPBase.make_not_authenticated_error)."""
    async def override_get_db():
        yield mock_db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/reservas", json=_valid_payload())
        assert response.status_code == 401
    finally:
        app.dependency_overrides.clear()


def _build_reserva(*, estado: str, check_out: datetime, created_at: datetime) -> Reserva:
    return Reserva(
        id=uuid.uuid4(),
        check_in=check_out - timedelta(days=2),
        check_out=check_out,
        estado=estado,
        personas=2,
        viajero_id=USER_ID,
        habitaciones_ids=[HABITACION_ID],
        pago_id=None,
        created_at=created_at,
    )


@pytest.mark.asyncio
async def test_get_reservas_usuario_activas_returns_200(override_client, mock_db_session):
    now = datetime.now(UTC)
    reservas = [
        _build_reserva(
            estado="confirmada",
            check_out=now + timedelta(days=3),
            created_at=now,
        )
    ]

    result = MagicMock()
    scalar_result = MagicMock()
    scalar_result.all.return_value = reservas
    result.scalars.return_value = scalar_result
    mock_db_session.execute = AsyncMock(return_value=result)

    detalles = {
        HABITACION_ID: HabitacionReservaDetalleResponse(
            id=HABITACION_ID,
            nombre_habitacion="Deluxe Room",
            nombre_hotel="Grand Hyatt Regency",
            imagenes_hotel=["https://cdn.example.com/hoteles/grand-hyatt-1.jpg"],
        )
    }

    with patch(
        "app.routers.reservas.obtener_detalles_habitaciones_por_ids",
        new=AsyncMock(return_value=detalles),
    ):
        response = await override_client.get("/reservas?estado=activas")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert len(data["reservas"]) == 1
    assert data["reservas"][0]["estado"] == "confirmada"
    assert data["reservas"][0]["nombre_habitacion"] == "Deluxe Room"
    assert data["reservas"][0]["nombre_hotel"] == "Grand Hyatt Regency"
    assert data["reservas"][0]["imagenes_hotel"] == ["https://cdn.example.com/hoteles/grand-hyatt-1.jpg"]
    assert mock_db_session.execute.await_count == 1


@pytest.mark.asyncio
async def test_get_reservas_usuario_activas_orders_by_fecha_entrada(override_client, mock_db_session):
    now = datetime.now(UTC)
    reserva_tardia = _build_reserva(
        estado="confirmada",
        check_out=now + timedelta(days=10),
        created_at=now + timedelta(minutes=10),
    )
    reserva_temprana = _build_reserva(
        estado="pendiente",
        check_out=now + timedelta(days=5),
        created_at=now,
    )

    reservas = [reserva_tardia, reserva_temprana]

    result = MagicMock()
    scalar_result = MagicMock()
    scalar_result.all.return_value = reservas
    result.scalars.return_value = scalar_result
    mock_db_session.execute = AsyncMock(return_value=result)

    detalles = {
        HABITACION_ID: HabitacionReservaDetalleResponse(
            id=HABITACION_ID,
            nombre_habitacion="Deluxe Room",
            nombre_hotel="Grand Hyatt Regency",
            imagenes_hotel=["https://cdn.example.com/hoteles/grand-hyatt-1.jpg"],
        )
    }

    with patch(
        "app.routers.reservas.obtener_detalles_habitaciones_por_ids",
        new=AsyncMock(return_value=detalles),
    ):
        response = await override_client.get("/reservas?estado=activas")

    assert response.status_code == 200
    data = response.json()
    assert [reserva["fecha_entrada"] for reserva in data["reservas"]] == [
        reserva_temprana.check_in.date().isoformat(),
        reserva_tardia.check_in.date().isoformat(),
    ]


@pytest.mark.asyncio
async def test_get_reservas_usuario_canceladas_returns_200(override_client, mock_db_session):
    now = datetime.now(UTC)
    reservas = [
        _build_reserva(
            estado="cancelada",
            check_out=now + timedelta(days=1),
            created_at=now,
        )
    ]

    result = MagicMock()
    scalar_result = MagicMock()
    scalar_result.all.return_value = reservas
    result.scalars.return_value = scalar_result
    mock_db_session.execute = AsyncMock(return_value=result)

    detalles = {
        HABITACION_ID: HabitacionReservaDetalleResponse(
            id=HABITACION_ID,
            nombre_habitacion="Junior Suite",
            nombre_hotel="Aman Tokyo Resort",
            imagenes_hotel=[
                "https://cdn.example.com/hoteles/aman-tokyo-1.jpg",
                "https://cdn.example.com/hoteles/aman-tokyo-2.jpg",
            ],
        )
    }

    with patch(
        "app.routers.reservas.obtener_detalles_habitaciones_por_ids",
        new=AsyncMock(return_value=detalles),
    ):
        response = await override_client.get("/reservas?estado=canceladas")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["reservas"][0]["estado"] == "cancelada"
    assert data["reservas"][0]["nombre_habitacion"] == "Junior Suite"
    assert data["reservas"][0]["nombre_hotel"] == "Aman Tokyo Resort"
    assert data["reservas"][0]["imagenes_hotel"] == [
        "https://cdn.example.com/hoteles/aman-tokyo-1.jpg",
        "https://cdn.example.com/hoteles/aman-tokyo-2.jpg",
    ]


@pytest.mark.asyncio
async def test_get_reservas_usuario_401_missing_authorization(mock_db_session):
    async def override_get_db():
        yield mock_db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/reservas?estado=activas")

        assert response.status_code == 401
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_reservas_hotel_returns_200(override_client, mock_db_session):
    now = datetime.now(UTC)
    reservas = [
        _build_reserva(
            estado="confirmada",
            check_out=now + timedelta(days=1),
            created_at=now,
        )
    ]

    result = MagicMock()
    scalar_result = MagicMock()
    scalar_result.all.return_value = reservas
    result.scalars.return_value = scalar_result
    mock_db_session.execute = AsyncMock(return_value=result)

    habitaciones = [
        HabitacionHotelResponse(
            id=HABITACION_ID,
            capacidad=2,
            numero="101",
            descripcion="Vista al mar",
            imagenes=[],
            monto=100,
            impuestos=10,
            disponible=True,
        )
    ]

    with patch("app.routers.reservas.obtener_habitaciones_hotel", new=AsyncMock(return_value=habitaciones)):
        response = await override_client.get("/reservas/hoteles")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert len(data["reservas"]) == 1
    assert len(data["habitaciones"]) == 1
    assert data["reservas"][0]["habitacion_id"] == str(HABITACION_ID)


@pytest.mark.asyncio
async def test_get_reservas_hotel_401_missing_authorization(mock_db_session):
    async def override_get_db():
        yield mock_db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/reservas/hoteles")

        assert response.status_code == 401
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_reserva_detalle_returns_200(override_client, mock_db_session):
    now = datetime.now(UTC)
    reserva = _build_reserva(
        estado="confirmada",
        check_out=now + timedelta(days=3),
        created_at=now,
    )
    mock_db_session.execute = AsyncMock(return_value=_execute_result_with_reserva(reserva))

    detalles = {
        HABITACION_ID: HabitacionReservaDetalleResponse(
            id=HABITACION_ID,
            nombre_habitacion="Deluxe King Room",
            nombre_hotel="Grand Hyatt Singapore",
            imagenes_hotel=["https://cdn.example.com/hoteles/grand-hyatt.jpg"],
            hotel_id=uuid.UUID("00000000-0000-4000-8000-000000000010"),
            direccion_hotel="10 Scotts Rd",
            ciudad_hotel="Singapore",
            pais_hotel="Singapore",
            estrellas_hotel=5,
            ranking_hotel=4.7,
            contacto_celular_hotel="+65 6738 1234",
            contacto_email_hotel="singapore.grand@hyatt.com",
            amenidades_hotel=["WIFI", "BREAKFAST_INCLUDED"],
            capacidad_habitacion=2,
            numero_habitacion="405",
            descripcion_habitacion="Deluxe King Room",
            imagenes_habitacion=["https://cdn.example.com/habitaciones/405.jpg"],
            monto_habitacion=450,
            impuestos_habitacion=80,
        )
    }

    with patch(
        "app.routers.reservas.obtener_detalles_habitaciones_por_ids",
        new=AsyncMock(return_value=detalles),
    ):
        response = await override_client.get(f"/reservas/{reserva.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(reserva.id)
    assert data["estado"] == "confirmada"
    assert data["hotel"]["nombre"] == "Grand Hyatt Singapore"
    assert data["hotel"]["direccion"] == "10 Scotts Rd"
    assert data["habitacion"]["nombre"] == "Deluxe King Room"
    assert data["amenidades_hotel"] == ["WIFI", "BREAKFAST_INCLUDED"]


@pytest.mark.asyncio
async def test_get_reserva_detalle_404_when_reserva_not_found(override_client, mock_db_session):
    mock_db_session.execute = AsyncMock(return_value=_execute_result_no_conflict())

    response = await override_client.get(f"/reservas/{uuid.uuid4()}")

    assert response.status_code == 404
    data = response.json()
    assert data["error"] == "not_found"


@pytest.mark.asyncio
async def test_get_reserva_detalle_401_missing_authorization(mock_db_session):
    async def override_get_db():
        yield mock_db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(f"/reservas/{uuid.uuid4()}")

        assert response.status_code == 401
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_patch_reserva_cancelar_returns_200(override_client, mock_db_session):
    now = datetime.now(UTC)
    reserva = _build_reserva(
        estado="confirmada",
        check_out=now + timedelta(days=2),
        created_at=now,
    )
    mock_db_session.execute = AsyncMock(return_value=_execute_result_with_reserva(reserva))

    response = await override_client.patch(f"/reservas/{reserva.id}/cancelar")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(reserva.id)
    assert data["estado"] == "cancelada"
    assert mock_db_session.commit.await_count == 1
    assert mock_db_session.refresh.await_count == 1


@pytest.mark.asyncio
async def test_patch_reserva_cancelar_404_when_reserva_not_found(override_client, mock_db_session):
    mock_db_session.execute = AsyncMock(return_value=_execute_result_no_conflict())

    response = await override_client.patch(f"/reservas/{uuid.uuid4()}/cancelar")

    assert response.status_code == 404
    data = response.json()
    assert data["error"] == "not_found"


@pytest.mark.asyncio
async def test_patch_reserva_cancelar_409_when_already_cancelada(override_client, mock_db_session):
    now = datetime.now(UTC)
    reserva = _build_reserva(
        estado="cancelada",
        check_out=now + timedelta(days=1),
        created_at=now,
    )
    mock_db_session.execute = AsyncMock(return_value=_execute_result_with_reserva(reserva))

    response = await override_client.patch(f"/reservas/{reserva.id}/cancelar")

    assert response.status_code == 409
    data = response.json()
    assert "cancelada" in data["detail"].lower()


@pytest.mark.asyncio
async def test_patch_reserva_cancelar_401_missing_authorization(mock_db_session):
    async def override_get_db():
        yield mock_db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.patch(f"/reservas/{uuid.uuid4()}/cancelar")

        assert response.status_code == 401
    finally:
        app.dependency_overrides.clear()
