"""Pruebas de API pagos."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID

import pytest
from httpx import ASGITransport, AsyncClient

from app.config import Settings, get_settings
from app.database import get_db
from app.main import app
from app.models.pago import EstadoPago
from travelhub_common.security import RoleEnum, User, get_current_user

USER_ID = UUID("aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee")

CARD_FIELDS = {
    "numero": "4111111111111111",
    "cvv": "123",
    "fecha_expiracion": "12/2099",
}


@pytest.fixture
def mock_db_session():
    session = AsyncMock()
    session.add = MagicMock()
    session.flush = AsyncMock()

    async def mock_refresh(instance, attribute_names=None):
        from uuid import uuid4

        if getattr(instance, "id", None) is None:
            instance.id = uuid4()
        now = datetime.now(UTC)
        if getattr(instance, "created_at", None) is None:
            instance.created_at = now
        instance.updated_at = now

    session.refresh = AsyncMock(side_effect=mock_refresh)
    session.commit = AsyncMock()
    return session


@pytest.fixture
def pagos_app_settings():
    return Settings(
        environment="test",
        service_name="pagos",
        db_url="postgresql+asyncpg://test:test@localhost/test",
        jwt_public_key="dummy",
    )


@pytest.fixture
async def client_pagos(mock_db_session, pagos_app_settings):
    async def override_get_db():
        yield mock_db_session

    def override_user():
        return User(
            id=USER_ID,
            email="u@test.com",
            role=RoleEnum.USER,
        )

    def override_settings():
        return pagos_app_settings

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_user
    app.dependency_overrides[get_settings] = override_settings

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()
    get_settings.cache_clear()


@pytest.mark.asyncio
async def test_post_pagar_422_medio_de_pago_solo_espacios(client_pagos):
    response = await client_pagos.post(
        "/pagos/pagar",
        json={
            "monto": 1000,
            "medio_de_pago": "   ",
            "debe_fallar": False,
            **CARD_FIELDS,
        },
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_post_pagar_201_successful(client_pagos, mock_db_session):
    reserva_id = UUID("11111111-2222-4333-8444-555555555555")
    reserva_detalle = MagicMock()
    reserva_detalle.id = reserva_id
    reserva_detalle.viajero_id = USER_ID
    reserva_detalle.codigo_reserva = "TH-11111111"
    reserva_detalle.fecha_entrada = datetime(2026, 7, 10, tzinfo=UTC).date()
    reserva_detalle.fecha_salida = datetime(2026, 7, 15, tzinfo=UTC).date()
    reserva_detalle.num_huespedes = 2
    reserva_detalle.hotel = MagicMock(nombre="Hotel Aurora")
    reserva_detalle.habitacion = MagicMock(nombre="Suite Premium", numero="808")

    with patch(
        "app.services.pago_service.obtener_reserva_detalle_para_pago",
        new=AsyncMock(return_value=reserva_detalle),
    ), patch("app.services.pago_service.send_booking_email") as mock_send_email:
        response = await client_pagos.post(
            "/pagos/pagar",
            json={
                "monto": 1000,
                "medio_de_pago": "  tarjeta_credito  ",
                "reserva_id": str(reserva_id),
                "debe_fallar": False,
                **CARD_FIELDS,
            },
        )

    assert response.status_code == 201, response.text
    data = response.json()
    assert data["monto"] == 1000
    assert data["medio_de_pago"] == "tarjeta_credito"
    assert data["estado"] == "successful"
    assert data["tarjeta_ultimos_4"] == "9999"
    assert mock_db_session.flush.await_count == 1
    assert mock_db_session.commit.await_count == 1
    mock_db_session.add.assert_called_once()
    mock_send_email.assert_called_once()
    payload = mock_send_email.call_args.args[0]
    assert payload.hotel_name == "Hotel Aurora"
    assert payload.room_name == "Suite Premium"
    assert payload.recipient_email == "u@test.com"


@pytest.mark.asyncio
async def test_post_pagar_skips_email_when_reservation_owned_by_different_user(client_pagos):
    reserva_id = UUID("11111111-2222-4333-8444-555555555555")
    reserva_detalle = MagicMock()
    reserva_detalle.id = reserva_id
    reserva_detalle.viajero_id = UUID("ffffffff-eeee-dddd-cccc-bbbbbbbbbbbb")
    reserva_detalle.codigo_reserva = "TH-11111111"
    reserva_detalle.fecha_entrada = datetime(2026, 7, 10, tzinfo=UTC).date()
    reserva_detalle.fecha_salida = datetime(2026, 7, 15, tzinfo=UTC).date()
    reserva_detalle.num_huespedes = 2
    reserva_detalle.hotel = MagicMock(nombre="Hotel Aurora")
    reserva_detalle.habitacion = MagicMock(nombre="Suite Premium", numero="808")

    with patch(
        "app.services.pago_service.obtener_reserva_detalle_para_pago",
        new=AsyncMock(return_value=reserva_detalle),
    ), patch("app.services.pago_service.send_booking_email") as mock_send_email:
        response = await client_pagos.post(
            "/pagos/pagar",
            json={
                "monto": 1000,
                "medio_de_pago": "tarjeta_credito",
                "reserva_id": str(reserva_id),
                "debe_fallar": False,
                **CARD_FIELDS,
            },
        )

    assert response.status_code == 201, response.text
    mock_send_email.assert_not_called()


@pytest.mark.asyncio
async def test_post_pagar_201_failed_flag(client_pagos):
    with patch("app.services.pago_service.send_booking_email") as mock_send_email:
        response = await client_pagos.post(
            "/pagos/pagar",
            json={
                "monto": 500,
                "medio_de_pago": "tarjeta_credito",
                "reserva_id": str(UUID("11111111-2222-4333-8444-555555555555")),
                "debe_fallar": True,
                **CARD_FIELDS,
            },
        )

    assert response.status_code == 201
    body = response.json()
    assert body["estado"] == "failed"
    assert body["tarjeta_ultimos_4"] == "9999"
    mock_send_email.assert_not_called()


@pytest.mark.asyncio
async def test_get_pago_200(client_pagos, mock_db_session):
    pago_id = UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb")
    now = datetime.now(UTC)
    pago = MagicMock()
    pago.id = pago_id
    pago.monto = 1500
    pago.medio_de_pago = "tarjeta_credito"
    pago.created_at = now
    pago.updated_at = now
    pago.estado = EstadoPago.successful
    pago.tarjeta_ultimos_4 = "9999"

    result = MagicMock()
    result.scalar_one_or_none.return_value = pago
    mock_db_session.execute = AsyncMock(return_value=result)

    response = await client_pagos.get(f"/pagos/{pago_id}")

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["id"] == str(pago_id)
    assert data["monto"] == 1500
    assert data["medio_de_pago"] == "tarjeta_credito"
    assert data["estado"] == "successful"
    assert data["tarjeta_ultimos_4"] == "9999"
    mock_db_session.execute.assert_awaited()


@pytest.mark.asyncio
async def test_get_pago_404(client_pagos, mock_db_session):
    pago_id = UUID("cccccccc-cccc-cccc-cccc-cccccccccccc")
    result = MagicMock()
    result.scalar_one_or_none.return_value = None
    mock_db_session.execute = AsyncMock(return_value=result)

    response = await client_pagos.get(f"/pagos/{pago_id}")

    assert response.status_code == 404
    body = response.json()
    assert body.get("error") == "not_found"
