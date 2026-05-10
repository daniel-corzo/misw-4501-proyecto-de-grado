import uuid
from datetime import date, datetime, timedelta, UTC
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock
from unittest.mock import patch

import pytest
from fastapi import HTTPException

from app.models.reserva import Reserva
from app.schemas.reserva import (
    CrearReservaRequest,
    HabitacionHotelResponse,
    HabitacionReservaDetalleResponse,
    ModificarReservaRequest,
    ReservaHotelResponse,
)
from app.services.reserva_service import (
    cancelar_reserva_service,
    construir_reservas_hotel_response,
    confirmar_reserva_service,
    crear_reserva_service,
    listar_reservas_usuario_service,
    listar_reservas_hotel_service,
    modificar_reserva_service,
    rechazar_reserva_service,
)
from travelhub_common.security import RoleEnum, User

USER_ID = uuid.uuid4()
OTHER_ID = uuid.uuid4()
HAB_ID = uuid.uuid4()
RESERVA_ID = uuid.uuid4()


def _execute_result_no_conflict():
    r = MagicMock()
    r.scalar_one_or_none.return_value = None
    return r


def _execute_result_with_reserva(reserva: Reserva):
    r = MagicMock()
    r.scalar_one_or_none.return_value = reserva
    return r


@pytest.fixture
def mock_db():
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


def _body():
    return CrearReservaRequest(
        habitacion_id=HAB_ID,
        fecha_entrada=date(2026, 6, 1),
        fecha_salida=date(2026, 6, 4),
        num_huespedes=1,
    )


def _build_reserva(estado: str) -> Reserva:
    now = datetime.now(UTC)
    return Reserva(
        id=uuid.uuid4(),
        check_in=now,
        check_out=now,
        estado=estado,
        personas=1,
        viajero_id=USER_ID,
        habitaciones_ids=[HAB_ID],
        pago_id=None,
        created_at=now,
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("role", [RoleEnum.USER, RoleEnum.ADMIN])
async def test_crear_reserva_service_uses_current_user_id(mock_db, role):
    body = _body()
    current = User(id=USER_ID, email="invalid-email.com", role=role)

    out = await crear_reserva_service(db=mock_db, body=body, current_user=current)

    assert out.habitacion_id == HAB_ID
    assert out.estado.value == "pendiente"
    mock_db.add.assert_called_once()
    assert mock_db.flush.await_count == 1
    assert mock_db.commit.await_count == 1
    assert mock_db.execute.await_count == 1


@pytest.mark.asyncio
async def test_crear_reserva_service_409_overlap_conflict(mock_db):
    conflict_result = MagicMock()
    conflict_result.scalar_one_or_none.return_value = uuid.uuid4()
    mock_db.execute = AsyncMock(return_value=conflict_result)

    body = _body()
    current = User(id=USER_ID, email="viajero@test.com", role=RoleEnum.USER)

    with pytest.raises(HTTPException) as exc:
        await crear_reserva_service(db=mock_db, body=body, current_user=current)

    assert exc.value.status_code == 409
    mock_db.add.assert_not_called()


@pytest.mark.asyncio
async def test_cancelar_reserva_service_success(mock_db):
    reserva = _build_reserva("confirmada")
    mock_db.execute = AsyncMock(return_value=_execute_result_with_reserva(reserva))
    current = User(id=USER_ID, email="viajero@test.com", role=RoleEnum.USER)

    out = await cancelar_reserva_service(
        db=mock_db,
        reserva_id=reserva.id,
        current_user=current,
    )

    assert out.estado.value == "cancelada"
    assert mock_db.commit.await_count == 1
    assert mock_db.refresh.await_count == 1


@pytest.mark.asyncio
async def test_cancelar_reserva_service_404_not_found(mock_db):
    mock_db.execute = AsyncMock(return_value=_execute_result_no_conflict())
    current = User(id=USER_ID, email="viajero@test.com", role=RoleEnum.USER)

    with pytest.raises(HTTPException) as exc:
        await cancelar_reserva_service(
            db=mock_db,
            reserva_id=uuid.uuid4(),
            current_user=current,
        )

    assert exc.value.status_code == 404
    assert mock_db.commit.await_count == 0


def _reserva_modificable(**kwargs):
    now = datetime.now(UTC)
    viajero_id = kwargs.get("viajero_id", USER_ID)
    estado = kwargs.get("estado", "pendiente")
    check_out = kwargs.get("check_out", now + timedelta(days=10))
    check_in = kwargs.get("check_in", now + timedelta(days=5))
    rid = kwargs.get("id", RESERVA_ID)
    habitaciones_ids = kwargs.get("habitaciones_ids", [HAB_ID])
    return Reserva(
        id=rid,
        check_in=check_in,
        check_out=check_out,
        estado=estado,
        personas=2,
        viajero_id=viajero_id,
        habitaciones_ids=habitaciones_ids,
        pago_id=None,
        created_at=now,
    )


def _hotel_reserva_response(reserva: Reserva) -> ReservaHotelResponse:
    return ReservaHotelResponse(
        id=reserva.id,
        habitacion_id=HAB_ID,
        nombre_habitacion="Suite",
        nombre_hotel="Hotel Demo",
        imagenes_hotel=[],
        ciudad_hotel=None,
        pais_hotel=None,
        fecha_entrada=reserva.check_in.date(),
        fecha_salida=reserva.check_out.date(),
        num_huespedes=reserva.personas,
        estado=reserva.estado,
        pago_id=reserva.pago_id,
        created_at=reserva.created_at,
        nombre_viajero="Alice",
        email_viajero="alice@example.com",
        numero_habitacion="101",
        total_noches=max((reserva.check_out.date() - reserva.check_in.date()).days, 0),
        monto_total=220,
        estado_pago="successful" if reserva.pago_id else None,
    )


@pytest.mark.asyncio
async def test_modificar_reserva_service_success(mock_db):
    reserva = _reserva_modificable()
    load_result = MagicMock()
    load_result.scalar_one_or_none.return_value = reserva
    no_conflict = MagicMock()
    no_conflict.scalar_one_or_none.return_value = None
    mock_db.execute = AsyncMock(side_effect=[load_result, no_conflict])

    current = User(id=USER_ID, email="viajero@test.com", role=RoleEnum.USER)
    body = ModificarReservaRequest(num_huespedes=4)

    out = await modificar_reserva_service(
        db=mock_db,
        reserva_id=RESERVA_ID,
        body=body,
        current_user=current,
    )

    assert out.personas == 4
    assert mock_db.flush.await_count == 1
    assert mock_db.commit.await_count == 1
    assert mock_db.execute.await_count == 2


@pytest.mark.asyncio
async def test_modificar_reserva_service_404_not_found(mock_db):
    load_result = MagicMock()
    load_result.scalar_one_or_none.return_value = None
    mock_db.execute = AsyncMock(return_value=load_result)

    current = User(id=USER_ID, email="viajero@test.com", role=RoleEnum.USER)
    body = ModificarReservaRequest(num_huespedes=3)

    with pytest.raises(HTTPException) as exc:
        await modificar_reserva_service(
            db=mock_db,
            reserva_id=RESERVA_ID,
            body=body,
            current_user=current,
        )

    assert exc.value.status_code == 404
    mock_db.commit.assert_not_called()


@pytest.mark.asyncio
async def test_cancelar_reserva_service_409_when_already_cancelled(mock_db):
    reserva = _build_reserva("cancelada")
    mock_db.execute = AsyncMock(return_value=_execute_result_with_reserva(reserva))
    current = User(id=USER_ID, email="viajero@test.com", role=RoleEnum.USER)

    with pytest.raises(HTTPException) as exc:
        await cancelar_reserva_service(
            db=mock_db,
            reserva_id=reserva.id,
            current_user=current,
        )

    assert exc.value.status_code == 409
    assert exc.value.detail == "La reserva ya está cancelada"
    assert mock_db.commit.await_count == 0


@pytest.mark.asyncio
async def test_confirmar_reserva_service_success(mock_db):
    reserva = _reserva_modificable(estado="pendiente")
    mock_db.execute = AsyncMock(return_value=_execute_result_with_reserva(reserva))

    out = await confirmar_reserva_service(
        db=mock_db,
        reserva_id=reserva.id,
        habitacion_ids_hotel=[HAB_ID],
    )

    assert out.estado == "confirmada"
    assert mock_db.flush.await_count == 1
    assert mock_db.commit.await_count == 1
    assert mock_db.refresh.await_count == 1


@pytest.mark.asyncio
async def test_confirmar_reserva_service_404_if_room_not_owned(mock_db):
    reserva = _reserva_modificable(habitaciones_ids=[uuid.uuid4()])
    mock_db.execute = AsyncMock(return_value=_execute_result_with_reserva(reserva))

    with pytest.raises(HTTPException) as exc:
        await confirmar_reserva_service(
            db=mock_db,
            reserva_id=reserva.id,
            habitacion_ids_hotel=[HAB_ID],
        )

    assert exc.value.status_code == 404
    mock_db.commit.assert_not_called()


@pytest.mark.asyncio
async def test_construir_reservas_hotel_response_enriches_data():
    reserva = _reserva_modificable(estado="confirmada")
    reserva.pago_id = uuid.uuid4()

    detalles = {
        HAB_ID: HabitacionReservaDetalleResponse(
            id=HAB_ID,
            nombre_habitacion="Deluxe King Suite",
            nombre_hotel="Grand Palace",
            imagenes_hotel=[],
            numero_habitacion="101",
            monto_habitacion=100,
            impuestos_habitacion=10,
        )
    }

    with patch(
        "app.services.reserva_service.obtener_detalles_habitaciones_por_ids",
        new=AsyncMock(return_value=detalles),
    ), patch(
        "app.services.reserva_service.obtener_usuarios_resumen_por_ids",
        new=AsyncMock(
            return_value={
                USER_ID: SimpleNamespace(
                    id=USER_ID,
                    nombre="Johnathan Doe",
                    email="johnathan@example.com",
                )
            }
        ),
    ), patch(
        "app.services.reserva_service.obtener_pagos_por_ids",
        new=AsyncMock(
            return_value={
                reserva.pago_id: SimpleNamespace(
                    id=reserva.pago_id,
                    estado="successful",
                )
            }
        ),
    ):
        response = await construir_reservas_hotel_response("Bearer token", [reserva])

    assert len(response) == 1
    hotel_reserva = response[0]
    assert hotel_reserva.nombre_viajero == "Johnathan Doe"
    assert hotel_reserva.email_viajero == "johnathan@example.com"
    assert hotel_reserva.nombre_habitacion == "Deluxe King Suite"
    assert hotel_reserva.numero_habitacion == "101"
    assert hotel_reserva.estado_pago.value == "successful"
    assert hotel_reserva.monto_total == 550
    assert hotel_reserva.total_noches == 5


@pytest.mark.asyncio
async def test_listar_reservas_hotel_service_applies_pagination_and_order(mock_db):
    now = datetime.now(UTC)
    reserva = _reserva_modificable(
        estado="confirmada",
        check_in=now + timedelta(days=3),
        check_out=now + timedelta(days=5),
    )

    count_result = MagicMock()
    count_result.scalar_one.return_value = 24
    list_result = MagicMock()
    list_scalar_result = MagicMock()
    list_scalar_result.all.return_value = [reserva]
    list_result.scalars.return_value = list_scalar_result
    mock_db.execute = AsyncMock(side_effect=[count_result, list_result])

    habitaciones = [
        HabitacionHotelResponse(
            id=HAB_ID,
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
        "app.services.reserva_service.obtener_habitaciones_hotel",
        new=AsyncMock(return_value=habitaciones),
    ), patch(
        "app.services.reserva_service.construir_reservas_hotel_response",
        new=AsyncMock(return_value=[_hotel_reserva_response(reserva)]),
    ):
        response = await listar_reservas_hotel_service(
            db=mock_db,
            authorization_header="Bearer token",
            skip=10,
            limit=5,
        )

    assert response.total == 24
    assert len(response.reservas) == 1
    assert len(response.habitaciones) == 1
    executed_stmt = mock_db.execute.await_args_list[1].args[0]
    assert "check_in asc" in str(executed_stmt).lower()
    assert executed_stmt._limit_clause.value == 5
    assert executed_stmt._offset_clause.value == 10


@pytest.mark.asyncio
async def test_confirmar_reserva_service_409_wrong_state(mock_db):
    reserva = _reserva_modificable(estado="confirmada")
    mock_db.execute = AsyncMock(return_value=_execute_result_with_reserva(reserva))

    with pytest.raises(HTTPException) as exc:
        await confirmar_reserva_service(
            db=mock_db,
            reserva_id=reserva.id,
            habitacion_ids_hotel=[HAB_ID],
        )

    assert exc.value.status_code == 409
    assert mock_db.commit.await_count == 0


@pytest.mark.asyncio
@pytest.mark.parametrize("estado", ["pendiente", "confirmada"])
async def test_rechazar_reserva_service_success(mock_db, estado):
    reserva = _reserva_modificable(estado=estado)
    mock_db.execute = AsyncMock(return_value=_execute_result_with_reserva(reserva))

    out = await rechazar_reserva_service(
        db=mock_db,
        reserva_id=reserva.id,
        habitacion_ids_hotel=[HAB_ID],
    )

    assert out.estado == "cancelada"
    assert mock_db.flush.await_count == 1
    assert mock_db.commit.await_count == 1
    assert mock_db.refresh.await_count == 1


@pytest.mark.asyncio
async def test_rechazar_reserva_service_404_if_room_not_owned(mock_db):
    reserva = _reserva_modificable(habitaciones_ids=[uuid.uuid4()])
    mock_db.execute = AsyncMock(return_value=_execute_result_with_reserva(reserva))

    with pytest.raises(HTTPException) as exc:
        await rechazar_reserva_service(
            db=mock_db,
            reserva_id=reserva.id,
            habitacion_ids_hotel=[HAB_ID],
        )

    assert exc.value.status_code == 404
    mock_db.commit.assert_not_called()


@pytest.mark.asyncio
async def test_rechazar_reserva_service_409_when_already_cancelled(mock_db):
    reserva = _reserva_modificable(estado="cancelada")
    mock_db.execute = AsyncMock(return_value=_execute_result_with_reserva(reserva))

    with pytest.raises(HTTPException) as exc:
        await rechazar_reserva_service(
            db=mock_db,
            reserva_id=reserva.id,
            habitacion_ids_hotel=[HAB_ID],
        )

    assert exc.value.status_code == 409
    assert exc.value.detail == "La reserva ya está cancelada"
    mock_db.commit.assert_not_called()


@pytest.mark.asyncio
async def test_modificar_reserva_service_404_wrong_user(mock_db):
    reserva = _reserva_modificable(viajero_id=uuid.uuid4())
    load_result = MagicMock()
    load_result.scalar_one_or_none.return_value = reserva
    mock_db.execute = AsyncMock(return_value=load_result)

    current = User(id=USER_ID, email="viajero@test.com", role=RoleEnum.USER)
    body = ModificarReservaRequest(num_huespedes=3)

    with pytest.raises(HTTPException) as exc:
        await modificar_reserva_service(
            db=mock_db,
            reserva_id=RESERVA_ID,
            body=body,
            current_user=current,
        )

    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_modificar_reserva_service_409_estado(mock_db):
    reserva = _reserva_modificable(estado="cancelada")
    load_result = MagicMock()
    load_result.scalar_one_or_none.return_value = reserva
    mock_db.execute = AsyncMock(return_value=load_result)

    current = User(id=USER_ID, email="viajero@test.com", role=RoleEnum.USER)
    body = ModificarReservaRequest(num_huespedes=3)

    with pytest.raises(HTTPException) as exc:
        await modificar_reserva_service(
            db=mock_db,
            reserva_id=RESERVA_ID,
            body=body,
            current_user=current,
        )

    assert exc.value.status_code == 409


@pytest.mark.asyncio
async def test_listar_reservas_usuario_service(mock_db):
    current = User(id=USER_ID, email="user@test.com", role=RoleEnum.USER)

    mock_db.execute = AsyncMock()
    mock_count_result = MagicMock()
    mock_count_result.scalar_one.return_value = 1

    mock_reserva = MagicMock()
    mock_reserva.id = uuid.uuid4()
    mock_reserva.viajero_id = USER_ID
    mock_reserva.habitaciones_ids = [HAB_ID]
    mock_reserva.check_in = datetime.now()
    mock_reserva.check_out = datetime.now()
    mock_reserva.personas = 2
    mock_reserva.estado = "confirmada"
    mock_reserva.pago_id = None
    mock_reserva.created_at = datetime.now(UTC)

    mock_list_result = MagicMock()
    mock_list_result.scalars().all.return_value = [mock_reserva]

    mock_db.execute.side_effect = [mock_count_result, mock_list_result]

    response = await listar_reservas_usuario_service(
        db=mock_db, usuario_id=USER_ID, skip=0, limit=10, current_user=current
    )

    assert response.total == 1
    assert len(response.reservas) == 1
    assert response.reservas[0].id == mock_reserva.id


@pytest.mark.asyncio
async def test_listar_reservas_usuario_forbidden(mock_db):
    current = User(id=USER_ID, email="user@test.com", role=RoleEnum.USER)

    with pytest.raises(HTTPException) as exc:
        await listar_reservas_usuario_service(
            db=mock_db, usuario_id=OTHER_ID, skip=0, limit=10, current_user=current
        )

    assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_listar_reservas_usuario_service_admin_puede_ver_otros_usuarios(mock_db):
    admin = User(id=USER_ID, email="admin@test.com", role=RoleEnum.ADMIN)

    mock_count_result = MagicMock()
    mock_count_result.scalar_one.return_value = 1

    mock_reserva = MagicMock()
    mock_reserva.id = uuid.uuid4()
    mock_reserva.viajero_id = OTHER_ID
    mock_reserva.habitaciones_ids = [HAB_ID]
    mock_reserva.check_in = datetime.now(UTC)
    mock_reserva.check_out = datetime.now(UTC)
    mock_reserva.personas = 1
    mock_reserva.estado = "confirmada"
    mock_reserva.pago_id = None
    mock_reserva.created_at = datetime.now(UTC)

    mock_list_result = MagicMock()
    mock_list_result.scalars().all.return_value = [mock_reserva]

    mock_db.execute = AsyncMock(side_effect=[mock_count_result, mock_list_result])

    response = await listar_reservas_usuario_service(
        db=mock_db, usuario_id=OTHER_ID, skip=0, limit=10, current_user=admin
    )

    assert response.total == 1
    assert len(response.reservas) == 1
    assert response.reservas[0].id == mock_reserva.id


@pytest.mark.asyncio
async def test_modificar_reserva_service_400_past(mock_db):
    now = datetime.now(UTC)
    reserva = _reserva_modificable(
        check_in=now - timedelta(days=5),
        check_out=now - timedelta(days=1),
    )
    load_result = MagicMock()
    load_result.scalar_one_or_none.return_value = reserva
    mock_db.execute = AsyncMock(return_value=load_result)

    current = User(id=USER_ID, email="viajero@test.com", role=RoleEnum.USER)
    body = ModificarReservaRequest(num_huespedes=3)

    with pytest.raises(HTTPException) as exc:
        await modificar_reserva_service(
            db=mock_db,
            reserva_id=RESERVA_ID,
            body=body,
            current_user=current,
        )

    assert exc.value.status_code == 400


@pytest.mark.asyncio
async def test_modificar_reserva_service_409_overlap(mock_db):
    reserva = _reserva_modificable()
    load_result = MagicMock()
    load_result.scalar_one_or_none.return_value = reserva
    conflict_result = MagicMock()
    conflict_result.scalar_one_or_none.return_value = uuid.uuid4()
    mock_db.execute = AsyncMock(side_effect=[load_result, conflict_result])

    current = User(id=USER_ID, email="viajero@test.com", role=RoleEnum.USER)
    body = ModificarReservaRequest(habitacion_id=uuid.uuid4())

    with pytest.raises(HTTPException) as exc:
        await modificar_reserva_service(
            db=mock_db,
            reserva_id=RESERVA_ID,
            body=body,
            current_user=current,
        )

    assert exc.value.status_code == 409
    mock_db.commit.assert_not_called()


@pytest.mark.asyncio
async def test_modificar_reserva_service_400_fechas_invalidas(mock_db):
    reserva = _reserva_modificable()
    load_result = MagicMock()
    load_result.scalar_one_or_none.return_value = reserva
    mock_db.execute = AsyncMock(return_value=load_result)

    salida_invalida = (reserva.check_in - timedelta(days=1)).date()
    body = ModificarReservaRequest(fecha_salida=salida_invalida)

    current = User(id=USER_ID, email="viajero@test.com", role=RoleEnum.USER)

    with pytest.raises(HTTPException) as exc:
        await modificar_reserva_service(
            db=mock_db,
            reserva_id=RESERVA_ID,
            body=body,
            current_user=current,
        )

    assert exc.value.status_code == 400
    mock_db.commit.assert_not_called()
