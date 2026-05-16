import uuid
from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock
from unittest.mock import patch

import pytest
from fastapi import HTTPException
from httpx import ASGITransport, AsyncClient

from app.database import get_db
from app.main import app
from app.schemas.reserva import (
    HabitacionHotelResponse,
    HabitacionReservaDetalleResponse,
    IngresoMensualResponse,
    ListaReservasHotelResponse,
    PagoReservaDetalleResponse,
    ReporteIngresosResponse,
    ReservaHabitacionDetalleCompletoResponse,
    ReservaHotelDetalleCompletoResponse,
    ReservaHotelDetalleResponse,
    ReservaHotelResponse,
    ViajeroReservaDetalleResponse,
)
from travelhub_common.security import RoleEnum, User, get_current_user
from app.models.reserva import Reserva

USER_ID = uuid.UUID("00000000-0000-4000-8000-000000000001")
OTHER_USER_ID = uuid.UUID("00000000-0000-4000-8000-000000000003")
HABITACION_ID = uuid.UUID("00000000-0000-4000-8000-000000000002")
PAGO_ID = uuid.UUID("00000000-0000-4000-8000-000000000004")


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


@pytest.fixture
async def override_manager_client(mock_db_session):
    async def override_get_db():
        yield mock_db_session

    def override_user():
        return User(
            id=USER_ID,
            email="manager@test.com",
            role=RoleEnum.MANAGER,
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


def _build_reserva(
    *,
    estado: str,
    check_out: datetime,
    created_at: datetime,
    viajero_id: uuid.UUID = USER_ID,
    pago_id: uuid.UUID | None = None,
    habitaciones_ids: list[uuid.UUID] | None = None,
) -> Reserva:
    return Reserva(
        id=uuid.uuid4(),
        check_in=check_out - timedelta(days=2),
        check_out=check_out,
        estado=estado,
        personas=2,
        viajero_id=viajero_id,
        habitaciones_ids=habitaciones_ids or [HABITACION_ID],
        pago_id=pago_id,
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
        assert isinstance(data["reservas"], list)
        assert len(data["reservas"]) == 1
        assert data["reservas"][0]["estado"] == "confirmada"
        assert data["reservas"][0]["habitacion_id"] == str(HABITACION_ID)
        assert data["reservas"][0]["nombre_habitacion"] == "Deluxe Room"
        assert data["reservas"][0]["nombre_hotel"] == "Grand Hyatt Regency"
        assert data["reservas"][0]["imagenes_hotel"] == ["https://cdn.example.com/hoteles/grand-hyatt-1.jpg"]

@pytest.mark.asyncio
async def test_get_reservas_usuario_200(override_client, mock_db_session):
    mock_count_result = MagicMock()
    mock_count_result.scalar_one.return_value = 1
    
    mock_reserva = MagicMock()
    mock_reserva.id = uuid.uuid4()
    mock_reserva.viajero_id = USER_ID
    mock_reserva.habitaciones_ids = [HABITACION_ID]
    mock_reserva.check_in = datetime(2026, 5, 1, tzinfo=UTC)
    mock_reserva.check_out = datetime(2026, 5, 5, tzinfo=UTC)
    mock_reserva.personas = 2
    mock_reserva.estado = "pendiente"
    mock_reserva.pago_id = None
    mock_reserva.created_at = datetime.now(UTC)
    
    mock_list_result = MagicMock()
    mock_list_result.scalars().all.return_value = [mock_reserva]
    
    mock_db_session.execute = AsyncMock(side_effect=[mock_count_result, mock_list_result])
    
    response = await override_client.get(f"/reservas/usuario/{USER_ID}?skip=0&limit=10")
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert len(data["reservas"]) == 1
    assert data["reservas"][0]["estado"] == "pendiente"
    assert data["reservas"][0]["habitacion_id"] == str(HABITACION_ID)
    assert data["reservas"][0]["nombre_habitacion"] is None
    assert data["reservas"][0]["nombre_hotel"] is None
    assert data["reservas"][0]["imagenes_hotel"] == []
    assert mock_db_session.execute.await_count == 2


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
    assert data["total"] == 2
    assert isinstance(data["reservas"], list)
    assert len(data["reservas"]) == 2
    assert data["reservas"][0]["estado"] == "confirmada"
    assert data["reservas"][0]["habitacion_id"] == str(HABITACION_ID)
    assert data["reservas"][0]["nombre_habitacion"] == "Deluxe Room"
    assert data["reservas"][0]["nombre_hotel"] == "Grand Hyatt Regency"
    assert data["reservas"][0]["imagenes_hotel"] == ["https://cdn.example.com/hoteles/grand-hyatt-1.jpg"]


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
async def test_get_reservas_usuario_canceladas_orders_by_created_at_desc(override_client, mock_db_session):
    now = datetime.now(UTC)
    reserva_antigua = _build_reserva(
        estado="cancelada",
        check_out=now - timedelta(days=1),
        created_at=now,
    )
    reserva_reciente = _build_reserva(
        estado="cancelada",
        check_out=now - timedelta(days=2),
        created_at=now + timedelta(minutes=5),
    )

    result = MagicMock()
    scalar_result = MagicMock()
    scalar_result.all.return_value = [reserva_antigua, reserva_reciente]
    result.scalars.return_value = scalar_result
    mock_db_session.execute = AsyncMock(return_value=result)

    detalles = {
        HABITACION_ID: HabitacionReservaDetalleResponse(
            id=HABITACION_ID,
            nombre_habitacion="Junior Suite",
            nombre_hotel="Aman Tokyo Resort",
            imagenes_hotel=[],
        )
    }

    with patch(
        "app.routers.reservas.obtener_detalles_habitaciones_por_ids",
        new=AsyncMock(return_value=detalles),
    ):
        response = await override_client.get("/reservas?estado=canceladas")

    assert response.status_code == 200
    executed_stmt = mock_db_session.execute.await_args.args[0]
    assert "order by" in str(executed_stmt).lower()
    assert "created_at desc" in str(executed_stmt).lower()


@pytest.mark.asyncio
async def test_get_reservas_usuario_pasadas_orders_by_created_at_desc(override_client, mock_db_session):
    now = datetime.now(UTC)
    reserva_antigua = _build_reserva(
        estado="completada",
        check_out=now - timedelta(days=3),
        created_at=now,
    )
    reserva_reciente = _build_reserva(
        estado="confirmada",
        check_out=now - timedelta(days=1),
        created_at=now + timedelta(minutes=5),
    )

    result = MagicMock()
    scalar_result = MagicMock()
    scalar_result.all.return_value = [reserva_antigua, reserva_reciente]
    result.scalars.return_value = scalar_result
    mock_db_session.execute = AsyncMock(return_value=result)

    detalles = {
        HABITACION_ID: HabitacionReservaDetalleResponse(
            id=HABITACION_ID,
            nombre_habitacion="King Room",
            nombre_hotel="Park Hyatt",
            imagenes_hotel=[],
        )
    }

    with patch(
        "app.routers.reservas.obtener_detalles_habitaciones_por_ids",
        new=AsyncMock(return_value=detalles),
    ):
        response = await override_client.get("/reservas?estado=pasadas")

    assert response.status_code == 200
    executed_stmt = mock_db_session.execute.await_args.args[0]
    assert "order by" in str(executed_stmt).lower()
    assert "created_at desc" in str(executed_stmt).lower()


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
async def test_get_reservas_hotel_returns_200(override_manager_client, mock_db_session):
    now = datetime.now(UTC)

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

    hotel_reserva = ReservaHotelResponse(
        id=uuid.uuid4(),
        habitacion_id=HABITACION_ID,
        nombre_habitacion="Deluxe King Suite",
        nombre_hotel="Grand Palace",
        imagenes_hotel=[],
        ciudad_hotel=None,
        pais_hotel=None,
        fecha_entrada=now.date(),
        fecha_salida=(now + timedelta(days=2)).date(),
        num_huespedes=2,
        estado="confirmada",
        pago_id=PAGO_ID,
        created_at=now,
        nombre_viajero="Johnathan Doe",
        email_viajero="johnathan@example.com",
        numero_habitacion="101",
        total_noches=2,
        monto_total=220,
        estado_pago="successful",
    )

    service_response = ListaReservasHotelResponse(
        total=1,
        reservas=[hotel_reserva],
        habitaciones=habitaciones,
    )

    with patch(
        "app.routers.reservas.listar_reservas_hotel_service",
        new=AsyncMock(return_value=service_response),
    ):
        response = await override_manager_client.get("/reservas/hoteles?skip=0&limit=10")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert len(data["reservas"]) == 1
    assert len(data["habitaciones"]) == 1
    assert data["reservas"][0]["estado"] == "confirmada"
    assert data["reservas"][0]["habitacion_id"] == str(HABITACION_ID)
    assert data["reservas"][0]["nombre_viajero"] == "Johnathan Doe"
    assert data["reservas"][0]["email_viajero"] == "johnathan@example.com"
    assert data["reservas"][0]["numero_habitacion"] == "101"
    assert data["reservas"][0]["estado_pago"] == "successful"
    assert data["reservas"][0]["monto_total"] == 220
    assert data["reservas"][0]["total_noches"] == 2


@pytest.mark.asyncio
async def test_get_reservas_hotel_passes_pagination_to_service(override_manager_client, mock_db_session):
    service_response = ListaReservasHotelResponse(total=0, reservas=[], habitaciones=[])

    mock_service = AsyncMock(return_value=service_response)
    with patch("app.routers.reservas.listar_reservas_hotel_service", new=mock_service):
        response = await override_manager_client.get("/reservas/hoteles?skip=10&limit=5")

    assert response.status_code == 200
    assert mock_service.await_args.kwargs["db"] is mock_db_session
    assert mock_service.await_args.kwargs["authorization_header"] is None
    assert mock_service.await_args.kwargs["skip"] == 10
    assert mock_service.await_args.kwargs["limit"] == 5


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
async def test_get_reserva_hotel_detalle_returns_200(override_manager_client, mock_db_session):
    now = datetime.now(UTC)
    reserva_id = uuid.uuid4()
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
    service_response = ReservaHotelDetalleCompletoResponse(
        id=reserva_id,
        viajero_id=OTHER_USER_ID,
        codigo_reserva="TH-ABC123",
        estado="confirmada",
        fecha_entrada=now.date(),
        fecha_salida=(now + timedelta(days=2)).date(),
        num_huespedes=2,
        pago_id=PAGO_ID,
        created_at=now,
        hotel=ReservaHotelDetalleResponse(
            id=uuid.uuid4(),
            nombre="Grand Palace",
            direccion="Main street 123",
            ciudad="Bogota",
            pais="Colombia",
            imagenes=["https://cdn.example.com/hotel.jpg"],
            contacto_celular="+57 3000000000",
            contacto_email="hotel@example.com",
        ),
        habitacion=ReservaHabitacionDetalleCompletoResponse(
            id=HABITACION_ID,
            nombre="Deluxe King Suite",
            descripcion="Large room",
            numero="101",
            capacidad=2,
            imagenes=["https://cdn.example.com/room.jpg"],
            monto=100,
            impuestos=10,
        ),
        amenidades_hotel=["WIFI", "POOL"],
        viajero=ViajeroReservaDetalleResponse(
            id=OTHER_USER_ID,
            nombre="Alice Montgomery",
            email="alice@example.com",
        ),
        pago=PagoReservaDetalleResponse(
            id=PAGO_ID,
            estado="successful",
            monto=220,
            medio_de_pago="VISA",
            created_at=now,
            tarjeta_ultimos_4="4242",
        ),
        total_noches=2,
        monto_total=220,
        qr_checkin_payload='{"codigo_reserva":"TH-ABC123"}',
    )

    mock_service = AsyncMock(return_value=service_response)
    with patch(
        "app.routers.reservas.obtener_habitaciones_hotel",
        new=AsyncMock(return_value=habitaciones),
    ), patch(
        "app.routers.reservas.obtener_reserva_hotel_detalle_service",
        new=mock_service,
    ):
        response = await override_manager_client.get(f"/reservas/hoteles/{reserva_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(reserva_id)
    assert data["hotel"]["nombre"] == "Grand Palace"
    assert data["habitacion"]["nombre"] == "Deluxe King Suite"
    assert data["viajero"]["email"] == "alice@example.com"
    assert data["pago"]["estado"] == "successful"
    assert data["pago"]["tarjeta_ultimos_4"] == "4242"
    assert data["total_noches"] == 2
    assert data["qr_checkin_payload"] == '{"codigo_reserva":"TH-ABC123"}'
    assert mock_service.await_args.kwargs["db"] is mock_db_session
    assert mock_service.await_args.kwargs["authorization_header"] is None
    assert mock_service.await_args.kwargs["habitacion_ids_hotel"] == [HABITACION_ID]


@pytest.mark.asyncio
async def test_get_reserva_hotel_detalle_404_when_not_found(override_manager_client):
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

    with patch(
        "app.routers.reservas.obtener_habitaciones_hotel",
        new=AsyncMock(return_value=habitaciones),
    ), patch(
        "app.routers.reservas.obtener_reserva_hotel_detalle_service",
        new=AsyncMock(
            side_effect=HTTPException(
                status_code=404,
                detail="Reserva no encontrada",
            )
        ),
    ):
        response = await override_manager_client.get(f"/reservas/hoteles/{uuid.uuid4()}")

    assert response.status_code == 404
    assert response.json()["error"] == "not_found"


@pytest.mark.asyncio
async def test_get_reserva_hotel_detalle_401_missing_authorization(mock_db_session):
    async def override_get_db():
        yield mock_db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(f"/reservas/hoteles/{uuid.uuid4()}")

        assert response.status_code == 401
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_patch_reserva_confirmar_returns_200(override_manager_client, mock_db_session):
    now = datetime.now(UTC)
    reserva = _build_reserva(
        estado="pendiente",
        check_out=now + timedelta(days=2),
        created_at=now,
        viajero_id=OTHER_USER_ID,
        pago_id=PAGO_ID,
    )
    mock_db_session.execute = AsyncMock(return_value=_execute_result_with_reserva(reserva))

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

    hotel_reserva = ReservaHotelResponse(
        id=reserva.id,
        habitacion_id=HABITACION_ID,
        nombre_habitacion="Deluxe King Suite",
        nombre_hotel="Grand Palace",
        imagenes_hotel=[],
        ciudad_hotel=None,
        pais_hotel=None,
        fecha_entrada=reserva.check_in.date(),
        fecha_salida=reserva.check_out.date(),
        num_huespedes=reserva.personas,
        estado="confirmada",
        pago_id=PAGO_ID,
        created_at=reserva.created_at,
        nombre_viajero="Alice Montgomery",
        email_viajero="alice@example.com",
        numero_habitacion="101",
        total_noches=2,
        monto_total=220,
        estado_pago="successful",
    )

    with patch("app.routers.reservas.obtener_habitaciones_hotel", new=AsyncMock(return_value=habitaciones)), patch(
        "app.routers.reservas.construir_reservas_hotel_response",
        new=AsyncMock(return_value=[hotel_reserva]),
    ), patch("app.routers.reservas.enviar_correo_estado_reserva") as mock_email:
        response = await override_manager_client.patch(f"/reservas/{reserva.id}/confirmar")

    assert response.status_code == 200
    data = response.json()
    assert data["estado"] == "confirmada"
    assert data["nombre_viajero"] == "Alice Montgomery"
    assert mock_db_session.commit.await_count == 1
    mock_email.assert_called_once()


@pytest.mark.asyncio
async def test_patch_reserva_confirmar_404_when_room_not_owned(override_manager_client, mock_db_session):
    now = datetime.now(UTC)
    reserva = _build_reserva(
        estado="pendiente",
        check_out=now + timedelta(days=2),
        created_at=now,
        habitaciones_ids=[uuid.uuid4()],
    )
    mock_db_session.execute = AsyncMock(return_value=_execute_result_with_reserva(reserva))

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

    with patch("app.routers.reservas.obtener_habitaciones_hotel", new=AsyncMock(return_value=habitaciones)), patch(
        "app.routers.reservas.enviar_correo_estado_reserva"
    ) as mock_email:
        response = await override_manager_client.patch(f"/reservas/{reserva.id}/confirmar")

    assert response.status_code == 404
    assert response.json()["error"] == "not_found"
    mock_email.assert_not_called()


@pytest.mark.asyncio
async def test_patch_reserva_confirmar_409_wrong_state(override_manager_client, mock_db_session):
    now = datetime.now(UTC)
    reserva = _build_reserva(
        estado="confirmada",
        check_out=now + timedelta(days=2),
        created_at=now,
    )
    mock_db_session.execute = AsyncMock(return_value=_execute_result_with_reserva(reserva))

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

    with patch("app.routers.reservas.obtener_habitaciones_hotel", new=AsyncMock(return_value=habitaciones)), patch(
        "app.routers.reservas.enviar_correo_estado_reserva"
    ) as mock_email:
        response = await override_manager_client.patch(f"/reservas/{reserva.id}/confirmar")

    assert response.status_code == 409
    assert response.json()["detail"] == "La reserva no puede ser confirmada en su estado actual"
    mock_email.assert_not_called()


@pytest.mark.asyncio
async def test_patch_reserva_rechazar_returns_200(override_manager_client, mock_db_session):
    now = datetime.now(UTC)
    reserva = _build_reserva(
        estado="confirmada",
        check_out=now + timedelta(days=2),
        created_at=now,
        viajero_id=OTHER_USER_ID,
    )
    mock_db_session.execute = AsyncMock(return_value=_execute_result_with_reserva(reserva))

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

    hotel_reserva = ReservaHotelResponse(
        id=reserva.id,
        habitacion_id=HABITACION_ID,
        nombre_habitacion="Junior Suite",
        nombre_hotel="Grand Palace",
        imagenes_hotel=[],
        ciudad_hotel=None,
        pais_hotel=None,
        fecha_entrada=reserva.check_in.date(),
        fecha_salida=reserva.check_out.date(),
        num_huespedes=reserva.personas,
        estado="cancelada",
        pago_id=None,
        created_at=reserva.created_at,
        nombre_viajero="Robert Kovic",
        email_viajero="robert@example.com",
        numero_habitacion="101",
        total_noches=2,
        monto_total=220,
        estado_pago=None,
    )

    with patch("app.routers.reservas.obtener_habitaciones_hotel", new=AsyncMock(return_value=habitaciones)), patch(
        "app.routers.reservas.construir_reservas_hotel_response",
        new=AsyncMock(return_value=[hotel_reserva]),
    ), patch("app.routers.reservas.enviar_correo_estado_reserva") as mock_email:
        response = await override_manager_client.patch(f"/reservas/{reserva.id}/rechazar")

    assert response.status_code == 200
    assert response.json()["estado"] == "cancelada"
    assert mock_db_session.commit.await_count == 1
    mock_email.assert_called_once()


@pytest.mark.asyncio
async def test_patch_reserva_rechazar_409_when_already_cancelada(override_manager_client, mock_db_session):
    now = datetime.now(UTC)
    reserva = _build_reserva(
        estado="cancelada",
        check_out=now + timedelta(days=2),
        created_at=now,
    )
    mock_db_session.execute = AsyncMock(return_value=_execute_result_with_reserva(reserva))

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

    with patch("app.routers.reservas.obtener_habitaciones_hotel", new=AsyncMock(return_value=habitaciones)), patch(
        "app.routers.reservas.enviar_correo_estado_reserva"
    ) as mock_email:
        response = await override_manager_client.patch(f"/reservas/{reserva.id}/rechazar")

    assert response.status_code == 409
    assert response.json()["detail"] == "La reserva ya está cancelada"
    mock_email.assert_not_called()


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

    detalles = {
        HABITACION_ID: HabitacionReservaDetalleResponse(
            id=HABITACION_ID,
            nombre_habitacion="Junior Suite",
            nombre_hotel="Grand Palace",
            imagenes_hotel=[],
            numero_habitacion="101",
        )
    }

    with patch(
        "app.routers.reservas.obtener_detalles_habitaciones_por_ids",
        new=AsyncMock(return_value=detalles),
    ), patch("app.routers.reservas.enviar_correo_estado_reserva") as mock_email:
        response = await override_client.patch(f"/reservas/{reserva.id}/cancelar")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(reserva.id)
    assert data["estado"] == "cancelada"
    assert mock_db_session.commit.await_count == 1
    assert mock_db_session.refresh.await_count == 1
    mock_email.assert_called_once()


@pytest.mark.asyncio
async def test_patch_reserva_cancelar_404_when_reserva_not_found(override_client, mock_db_session):
    mock_db_session.execute = AsyncMock(return_value=_execute_result_no_conflict())

    with patch("app.routers.reservas.enviar_correo_estado_reserva") as mock_email:
        response = await override_client.patch(f"/reservas/{uuid.uuid4()}/cancelar")

    assert response.status_code == 404
    data = response.json()
    assert data["error"] == "not_found"
    mock_email.assert_not_called()


@pytest.mark.asyncio
async def test_patch_reserva_cancelar_409_when_already_cancelada(override_client, mock_db_session):
    now = datetime.now(UTC)
    reserva = _build_reserva(
        estado="cancelada",
        check_out=now + timedelta(days=1),
        created_at=now,
    )
    mock_db_session.execute = AsyncMock(return_value=_execute_result_with_reserva(reserva))

    with patch("app.routers.reservas.enviar_correo_estado_reserva") as mock_email:
        response = await override_client.patch(f"/reservas/{reserva.id}/cancelar")

    assert response.status_code == 409
    data = response.json()
    assert data["detail"] == "La reserva ya está cancelada"
    mock_email.assert_not_called()


@pytest.mark.asyncio
async def test_patch_reserva_200(override_client, mock_db_session):
    rid = uuid.uuid4()
    now = datetime.now(UTC)
    reserva = Reserva(
        id=rid,
        check_in=now + timedelta(days=1),
        check_out=now + timedelta(days=3),
        estado="pendiente",
        personas=2,
        viajero_id=USER_ID,
        habitaciones_ids=[HABITACION_ID],
        pago_id=None,
        created_at=now,
    )
    load_result = MagicMock()
    load_result.scalar_one_or_none.return_value = reserva
    no_conflict = MagicMock()
    no_conflict.scalar_one_or_none.return_value = None
    mock_db_session.execute = AsyncMock(side_effect=[load_result, no_conflict])

    detalles = {
        HABITACION_ID: HabitacionReservaDetalleResponse(
            id=HABITACION_ID,
            nombre_habitacion="Suite",
            nombre_hotel="Hotel Demo",
            imagenes_hotel=[],
        )
    }

    with patch(
        "app.routers.reservas.obtener_detalles_habitaciones_por_ids",
        new=AsyncMock(return_value=detalles),
    ):
        response = await override_client.patch(
            f"/reservas/{rid}",
            json={"num_huespedes": 3},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["num_huespedes"] == 3
    assert mock_db_session.commit.await_count == 1


@pytest.mark.asyncio
async def test_patch_reserva_422_empty_body(override_client):
    rid = uuid.uuid4()
    response = await override_client.patch(f"/reservas/{rid}", json={})

    assert response.status_code == 422


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


@pytest.mark.asyncio
async def test_patch_reserva_401_missing_authorization(mock_db_session):
    async def override_get_db():
        yield mock_db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            rid = uuid.uuid4()
            response = await client.patch(
                f"/reservas/{rid}",
                json={"num_huespedes": 2},
            )

        assert response.status_code == 401
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_patch_reserva_confirmar_401_missing_authorization(mock_db_session):
    async def override_get_db():
        yield mock_db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.patch(f"/reservas/{uuid.uuid4()}/confirmar")

        assert response.status_code == 401
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_patch_reserva_rechazar_401_missing_authorization(mock_db_session):
    async def override_get_db():
        yield mock_db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.patch(f"/reservas/{uuid.uuid4()}/rechazar")

        assert response.status_code == 401
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_reservas_usuario_403(override_client):
    response = await override_client.get(f"/reservas/usuario/{OTHER_USER_ID}?skip=0&limit=10")

    assert response.status_code == 403
    assert response.json()["detail"] == "No tienes permiso para ver las reservas de este usuario"


@pytest.mark.asyncio
async def test_get_reservas_usuario_pasadas_returns_200(override_client, mock_db_session):
    now = datetime.now(UTC)
    reservas = [
        _build_reserva(
            estado="confirmada",
            check_out=now - timedelta(days=2),
            created_at=now - timedelta(days=5),
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
            nombre_habitacion="Classic Room",
            nombre_hotel="Hotel Boutique Paris",
            imagenes_hotel=["https://cdn.example.com/hoteles/paris-1.jpg"],
            ciudad_hotel="Paris",
            pais_hotel="France",
        )
    }

    with patch(
        "app.routers.reservas.obtener_detalles_habitaciones_por_ids",
        new=AsyncMock(return_value=detalles),
    ):
        response = await override_client.get("/reservas?estado=pasadas")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert isinstance(data["reservas"], list)
    assert len(data["reservas"]) == 1
    reserva = data["reservas"][0]
    assert reserva["estado"] == "confirmada"
    assert reserva["habitacion_id"] == str(HABITACION_ID)
    assert reserva["nombre_habitacion"] == "Classic Room"
    assert reserva["nombre_hotel"] == "Hotel Boutique Paris"
    assert reserva["imagenes_hotel"] == ["https://cdn.example.com/hoteles/paris-1.jpg"]
    assert reserva["ciudad_hotel"] == "Paris"
    assert reserva["pais_hotel"] == "France"


@pytest.mark.asyncio
async def test_get_reservas_activas_includes_ciudad_pais(override_client, mock_db_session):
    now = datetime.now(UTC)
    reservas = [
        _build_reserva(
            estado="confirmada",
            check_out=now + timedelta(days=5),
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
            imagenes_hotel=[],
            ciudad_hotel="Santorini",
            pais_hotel="Greece",
        )
    }

    with patch(
        "app.routers.reservas.obtener_detalles_habitaciones_por_ids",
        new=AsyncMock(return_value=detalles),
    ):
        response = await override_client.get("/reservas?estado=activas")

    assert response.status_code == 200
    data = response.json()
    reserva = data["reservas"][0]
    assert reserva["ciudad_hotel"] == "Santorini"
    assert reserva["pais_hotel"] == "Greece"


@pytest.mark.asyncio
async def test_get_reservas_activas_sql_excludes_cancelled_and_past(override_client, mock_db_session):
    now = datetime.now(UTC)
    result = MagicMock()
    scalar_result = MagicMock()
    scalar_result.all.return_value = []
    result.scalars.return_value = scalar_result
    mock_db_session.execute = AsyncMock(return_value=result)

    with patch(
        "app.routers.reservas.obtener_detalles_habitaciones_por_ids",
        new=AsyncMock(return_value={}),
    ):
        response = await override_client.get("/reservas?estado=activas")

    assert response.status_code == 200
    executed_stmt = mock_db_session.execute.await_args.args[0]
    stmt_str = str(executed_stmt).lower()
    assert "check_out" in stmt_str
    assert "order by" in stmt_str
    assert "check_in" in stmt_str


@pytest.mark.asyncio
async def test_get_reservas_pasadas_sql_excludes_canceladas(override_client, mock_db_session):
    result = MagicMock()
    scalar_result = MagicMock()
    scalar_result.all.return_value = []
    result.scalars.return_value = scalar_result
    mock_db_session.execute = AsyncMock(return_value=result)

    with patch(
        "app.routers.reservas.obtener_detalles_habitaciones_por_ids",
        new=AsyncMock(return_value={}),
    ):
        response = await override_client.get("/reservas?estado=pasadas")

    assert response.status_code == 200
    executed_stmt = mock_db_session.execute.await_args.args[0]
    stmt_str = str(executed_stmt).lower()
    assert "check_out" in stmt_str
    assert "created_at desc" in stmt_str


@pytest.mark.asyncio
async def test_get_reservas_estado_missing_returns_422(override_client):
    response = await override_client.get("/reservas")

    assert response.status_code == 422


# ---------------------------------------------------------------------------
# Filtros hotel: /reservas/hoteles query params
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_get_reservas_hotel_passes_nombre_viajero_to_service(override_manager_client, mock_db_session):
    service_response = ListaReservasHotelResponse(total=0, reservas=[], habitaciones=[])
    mock_service = AsyncMock(return_value=service_response)
    with patch("app.routers.reservas.listar_reservas_hotel_service", new=mock_service):
        response = await override_manager_client.get(
            "/reservas/hoteles?skip=0&limit=10&nombre_viajero=Alice"
        )

    assert response.status_code == 200
    assert mock_service.await_args.kwargs["nombre_viajero"] == "Alice"
    assert mock_service.await_args.kwargs["skip"] == 0
    assert mock_service.await_args.kwargs["limit"] == 10


@pytest.mark.asyncio
async def test_get_reservas_hotel_passes_tipo_habitacion_to_service(override_manager_client, mock_db_session):
    service_response = ListaReservasHotelResponse(total=0, reservas=[], habitaciones=[])
    mock_service = AsyncMock(return_value=service_response)
    with patch("app.routers.reservas.listar_reservas_hotel_service", new=mock_service):
        response = await override_manager_client.get(
            "/reservas/hoteles?tipo_habitacion=Suite"
        )

    assert response.status_code == 200
    assert mock_service.await_args.kwargs["tipo_habitacion"] == "Suite"


@pytest.mark.asyncio
async def test_get_reservas_hotel_passes_estado_to_service(override_manager_client, mock_db_session):
    service_response = ListaReservasHotelResponse(total=0, reservas=[], habitaciones=[])
    mock_service = AsyncMock(return_value=service_response)
    with patch("app.routers.reservas.listar_reservas_hotel_service", new=mock_service):
        response = await override_manager_client.get(
            "/reservas/hoteles?estado=confirmada"
        )

    assert response.status_code == 200
    from app.schemas.reserva import EstadoReserva
    assert mock_service.await_args.kwargs["estado"] == EstadoReserva.confirmada


@pytest.mark.asyncio
async def test_get_reservas_hotel_passes_date_range_to_service(override_manager_client, mock_db_session):
    from datetime import date
    service_response = ListaReservasHotelResponse(total=0, reservas=[], habitaciones=[])
    mock_service = AsyncMock(return_value=service_response)
    with patch("app.routers.reservas.listar_reservas_hotel_service", new=mock_service):
        response = await override_manager_client.get(
            "/reservas/hoteles?fecha_inicio=2026-06-01&fecha_fin=2026-06-30"
        )

    assert response.status_code == 200
    assert mock_service.await_args.kwargs["fecha_inicio"] == date(2026, 6, 1)
    assert mock_service.await_args.kwargs["fecha_fin"] == date(2026, 6, 30)


@pytest.mark.asyncio
async def test_get_reservas_hotel_passes_estado_pago_to_service(override_manager_client, mock_db_session):
    service_response = ListaReservasHotelResponse(total=0, reservas=[], habitaciones=[])
    mock_service = AsyncMock(return_value=service_response)
    with patch("app.routers.reservas.listar_reservas_hotel_service", new=mock_service):
        response = await override_manager_client.get(
            "/reservas/hoteles?estado_pago=pending"
        )

    assert response.status_code == 200
    from app.schemas.reserva import EstadoPagoFiltro
    assert mock_service.await_args.kwargs["estado_pago"] == EstadoPagoFiltro.pending


@pytest.mark.asyncio
async def test_get_reservas_hotel_passes_num_huespedes_to_service(override_manager_client, mock_db_session):
    service_response = ListaReservasHotelResponse(total=0, reservas=[], habitaciones=[])
    mock_service = AsyncMock(return_value=service_response)
    with patch("app.routers.reservas.listar_reservas_hotel_service", new=mock_service):
        response = await override_manager_client.get(
            "/reservas/hoteles?num_huespedes=3"
        )

    assert response.status_code == 200
    assert mock_service.await_args.kwargs["num_huespedes"] == 3


@pytest.mark.asyncio
async def test_get_reservas_hotel_invalid_estado_returns_422(override_manager_client, mock_db_session):
    response = await override_manager_client.get(
        "/reservas/hoteles?estado=invalido"
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_reservas_hotel_invalid_estado_pago_returns_422(override_manager_client, mock_db_session):
    response = await override_manager_client.get(
        "/reservas/hoteles?estado_pago=unknown_value"
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_reservas_hotel_filters_default_to_none(override_manager_client, mock_db_session):
    service_response = ListaReservasHotelResponse(total=0, reservas=[], habitaciones=[])
    mock_service = AsyncMock(return_value=service_response)
    with patch("app.routers.reservas.listar_reservas_hotel_service", new=mock_service):
        response = await override_manager_client.get("/reservas/hoteles")

    assert response.status_code == 200
    kwargs = mock_service.await_args.kwargs
    assert kwargs["nombre_viajero"] is None
    assert kwargs["tipo_habitacion"] is None
    assert kwargs["estado"] is None
    assert kwargs["fecha_inicio"] is None
    assert kwargs["fecha_fin"] is None
    assert kwargs["estado_pago"] is None
    assert kwargs["num_huespedes"] is None


# ---------------------------------------------------------------------------
# DELETE /reservas/{reserva_id}
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
@pytest.mark.parametrize("estado", ["pendiente", "cancelada"])
async def test_delete_reserva_204(override_client, mock_db_session, estado):
    """Owner can hard-delete a pendiente or cancelada reservation — returns 204."""
    now = datetime.now(UTC)
    reserva = _build_reserva(
        estado=estado,
        check_out=now + timedelta(days=2),
        created_at=now,
    )
    mock_db_session.execute = AsyncMock(return_value=_execute_result_with_reserva(reserva))
    mock_db_session.delete = AsyncMock()

    response = await override_client.delete(f"/reservas/{reserva.id}")

    assert response.status_code == 204
    assert response.content == b""
    mock_db_session.delete.assert_awaited_once_with(reserva)
    assert mock_db_session.commit.await_count == 1


@pytest.mark.asyncio
async def test_delete_reserva_404_not_found(override_client, mock_db_session):
    """Returns 404 when the reservation does not exist for the authenticated user."""
    mock_db_session.execute = AsyncMock(return_value=_execute_result_no_conflict())
    mock_db_session.delete = AsyncMock()

    response = await override_client.delete(f"/reservas/{uuid.uuid4()}")

    assert response.status_code == 404
    assert response.json()["error"] == "not_found"
    mock_db_session.delete.assert_not_called()
    mock_db_session.commit.assert_not_called()


@pytest.mark.asyncio
async def test_delete_reserva_409_confirmada(override_client, mock_db_session):
    """Returns 409 when trying to delete a confirmed reservation."""
    now = datetime.now(UTC)
    reserva = _build_reserva(
        estado="confirmada",
        check_out=now + timedelta(days=5),
        created_at=now,
    )
    mock_db_session.execute = AsyncMock(return_value=_execute_result_with_reserva(reserva))
    mock_db_session.delete = AsyncMock()

    response = await override_client.delete(f"/reservas/{reserva.id}")

    assert response.status_code == 409
    assert "pendientes o canceladas" in response.json()["detail"]
    mock_db_session.delete.assert_not_called()
    mock_db_session.commit.assert_not_called()


@pytest.mark.asyncio
async def test_delete_reserva_401_missing_authorization(mock_db_session):
    """Returns 401 when no Authorization header is present."""
    async def override_get_db():
        yield mock_db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.delete(f"/reservas/{uuid.uuid4()}")

        assert response.status_code == 401
    finally:
        app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# GET /reservas/hoteles/reporte-ingresos
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_reporte_ingresos_200(override_manager_client, mock_db_session):
    """Authenticated hotel manager receives a 200 with correct response shape."""
    reporte = ReporteIngresosResponse(
        nombre_hotel="Hotel Grand",
        ingresos_por_mes=[
            IngresoMensualResponse(anio=2026, mes=1, total_pagos=3, ingresos_totales=900),
            IngresoMensualResponse(anio=2026, mes=2, total_pagos=1, ingresos_totales=300),
        ],
        total_general=1200,
        total_pagos=4,
    )
    mock_service = AsyncMock(return_value=reporte)

    with patch("app.routers.reservas.generar_reporte_ingresos_service", new=mock_service):
        response = await override_manager_client.get("/reservas/hoteles/reporte-ingresos")

    assert response.status_code == 200
    body = response.json()
    assert body["nombre_hotel"] == "Hotel Grand"
    assert body["total_general"] == 1200
    assert body["total_pagos"] == 4
    assert len(body["ingresos_por_mes"]) == 2
    assert body["ingresos_por_mes"][0]["anio"] == 2026
    assert body["ingresos_por_mes"][0]["mes"] == 1
    assert body["ingresos_por_mes"][0]["total_pagos"] == 3
    assert body["ingresos_por_mes"][0]["ingresos_totales"] == 900


@pytest.mark.asyncio
async def test_reporte_ingresos_vacio_200(override_manager_client, mock_db_session):
    """Returns 200 with empty lists when the hotel has no payment history."""
    reporte = ReporteIngresosResponse(
        nombre_hotel=None,
        ingresos_por_mes=[],
        total_general=0,
        total_pagos=0,
    )
    mock_service = AsyncMock(return_value=reporte)

    with patch("app.routers.reservas.generar_reporte_ingresos_service", new=mock_service):
        response = await override_manager_client.get("/reservas/hoteles/reporte-ingresos")

    assert response.status_code == 200
    body = response.json()
    assert body["ingresos_por_mes"] == []
    assert body["total_general"] == 0


@pytest.mark.asyncio
async def test_reporte_ingresos_401_sin_autenticacion(mock_db_session):
    """Unauthenticated request to reporte-ingresos returns 401."""
    async def override_get_db():
        yield mock_db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/reservas/hoteles/reporte-ingresos")

        assert response.status_code == 401
    finally:
        app.dependency_overrides.clear()
