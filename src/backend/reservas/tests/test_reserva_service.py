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
    EstadoPagoFiltro,
    EstadoReserva,
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
    eliminar_reserva_service,
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
    ), patch(
        "app.services.reserva_service.obtener_detalles_habitaciones_por_ids",
        new=AsyncMock(return_value={}),
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
    assert response.habitaciones[0].nombre_habitacion is None
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


# ---------------------------------------------------------------------------
# Filtros: listar_reservas_hotel_service
# ---------------------------------------------------------------------------

def _make_habitaciones():
    return [
        HabitacionHotelResponse(
            id=HAB_ID,
            capacidad=2,
            numero="101",
            descripcion=None,
            imagenes=[],
            monto=100,
            impuestos=10,
            disponible=True,
        )
    ]


def _make_list_result(reservas_list):
    list_result = MagicMock()
    list_scalar = MagicMock()
    list_scalar.all.return_value = reservas_list
    list_result.scalars.return_value = list_scalar
    return list_result


@pytest.mark.asyncio
async def test_listar_reservas_hotel_service_sql_estado_filter(mock_db):
    """Estado filter goes to SQL (efficient path, 2 executes)."""
    reserva = _reserva_modificable(estado="confirmada")

    count_result = MagicMock()
    count_result.scalar_one.return_value = 1
    list_result = _make_list_result([reserva])
    mock_db.execute = AsyncMock(side_effect=[count_result, list_result])

    with patch(
        "app.services.reserva_service.obtener_habitaciones_hotel",
        new=AsyncMock(return_value=_make_habitaciones()),
    ), patch(
        "app.services.reserva_service.construir_reservas_hotel_response",
        new=AsyncMock(return_value=[_hotel_reserva_response(reserva)]),
    ), patch(
        "app.services.reserva_service.obtener_detalles_habitaciones_por_ids",
        new=AsyncMock(return_value={}),
    ):
        response = await listar_reservas_hotel_service(
            db=mock_db,
            authorization_header="Bearer token",
            skip=0,
            limit=10,
            estado=EstadoReserva.confirmada,
        )

    assert response.total == 1
    # SQL path: 2 executes (count + list)
    assert mock_db.execute.await_count == 2
    count_stmt = str(mock_db.execute.await_args_list[0].args[0]).lower()
    assert "estado" in count_stmt


@pytest.mark.asyncio
async def test_listar_reservas_hotel_service_sql_num_huespedes_filter(mock_db):
    """num_huespedes filter goes to SQL (efficient path, 2 executes)."""
    reserva = _reserva_modificable()

    count_result = MagicMock()
    count_result.scalar_one.return_value = 1
    list_result = _make_list_result([reserva])
    mock_db.execute = AsyncMock(side_effect=[count_result, list_result])

    with patch(
        "app.services.reserva_service.obtener_habitaciones_hotel",
        new=AsyncMock(return_value=_make_habitaciones()),
    ), patch(
        "app.services.reserva_service.construir_reservas_hotel_response",
        new=AsyncMock(return_value=[_hotel_reserva_response(reserva)]),
    ), patch(
        "app.services.reserva_service.obtener_detalles_habitaciones_por_ids",
        new=AsyncMock(return_value={}),
    ):
        response = await listar_reservas_hotel_service(
            db=mock_db,
            authorization_header="Bearer token",
            skip=0,
            limit=10,
            num_huespedes=2,
        )

    assert response.total == 1
    assert mock_db.execute.await_count == 2
    count_stmt = mock_db.execute.await_args_list[0].args[0]
    assert "personas" in str(count_stmt).lower()


@pytest.mark.asyncio
async def test_listar_reservas_hotel_service_sql_date_overlap_filter(mock_db):
    """fecha_inicio/fecha_fin filter goes to SQL (efficient path, 2 executes)."""
    from datetime import date as date_

    reserva = _reserva_modificable()

    count_result = MagicMock()
    count_result.scalar_one.return_value = 1
    list_result = _make_list_result([reserva])
    mock_db.execute = AsyncMock(side_effect=[count_result, list_result])

    with patch(
        "app.services.reserva_service.obtener_habitaciones_hotel",
        new=AsyncMock(return_value=_make_habitaciones()),
    ), patch(
        "app.services.reserva_service.construir_reservas_hotel_response",
        new=AsyncMock(return_value=[_hotel_reserva_response(reserva)]),
    ), patch(
        "app.services.reserva_service.obtener_detalles_habitaciones_por_ids",
        new=AsyncMock(return_value={}),
    ):
        response = await listar_reservas_hotel_service(
            db=mock_db,
            authorization_header="Bearer token",
            skip=0,
            limit=10,
            fecha_inicio=date_(2026, 6, 1),
            fecha_fin=date_(2026, 6, 30),
        )

    assert response.total == 1
    assert mock_db.execute.await_count == 2
    count_stmt = str(mock_db.execute.await_args_list[0].args[0]).lower()
    assert "check_in" in count_stmt or "check_out" in count_stmt


@pytest.mark.asyncio
async def test_listar_reservas_hotel_service_nombre_viajero_filter(mock_db):
    """nombre_viajero triggers in-memory path (1 SQL execute). Matching reservation passes."""
    reserva = _reserva_modificable()

    list_result = _make_list_result([reserva])
    mock_db.execute = AsyncMock(return_value=list_result)

    hotel_resp = _hotel_reserva_response(reserva)  # nombre_viajero="Alice"

    with patch(
        "app.services.reserva_service.obtener_habitaciones_hotel",
        new=AsyncMock(return_value=_make_habitaciones()),
    ), patch(
        "app.services.reserva_service.construir_reservas_hotel_response",
        new=AsyncMock(return_value=[hotel_resp]),
    ), patch(
        "app.services.reserva_service.obtener_detalles_habitaciones_por_ids",
        new=AsyncMock(return_value={}),
    ):
        response = await listar_reservas_hotel_service(
            db=mock_db,
            authorization_header="Bearer token",
            skip=0,
            limit=10,
            nombre_viajero="alice",
        )

    # In-memory path: 1 execute (no separate count query)
    assert mock_db.execute.await_count == 1
    assert response.total == 1
    assert len(response.reservas) == 1


@pytest.mark.asyncio
async def test_listar_reservas_hotel_service_nombre_viajero_no_match(mock_db):
    """nombre_viajero filter returns empty when no match."""
    reserva = _reserva_modificable()

    list_result = _make_list_result([reserva])
    mock_db.execute = AsyncMock(return_value=list_result)

    hotel_resp = _hotel_reserva_response(reserva)  # nombre_viajero="Alice"

    with patch(
        "app.services.reserva_service.obtener_habitaciones_hotel",
        new=AsyncMock(return_value=_make_habitaciones()),
    ), patch(
        "app.services.reserva_service.construir_reservas_hotel_response",
        new=AsyncMock(return_value=[hotel_resp]),
    ), patch(
        "app.services.reserva_service.obtener_detalles_habitaciones_por_ids",
        new=AsyncMock(return_value={}),
    ):
        response = await listar_reservas_hotel_service(
            db=mock_db,
            authorization_header="Bearer token",
            skip=0,
            limit=10,
            nombre_viajero="bob",
        )

    assert response.total == 0
    assert len(response.reservas) == 0


@pytest.mark.asyncio
async def test_listar_reservas_hotel_service_tipo_habitacion_filter(mock_db):
    """tipo_habitacion filters by nombre_habitacion substring (in-memory)."""
    reserva = _reserva_modificable()

    list_result = _make_list_result([reserva])
    mock_db.execute = AsyncMock(return_value=list_result)

    hotel_resp = _hotel_reserva_response(reserva)  # nombre_habitacion="Suite"

    with patch(
        "app.services.reserva_service.obtener_habitaciones_hotel",
        new=AsyncMock(return_value=_make_habitaciones()),
    ), patch(
        "app.services.reserva_service.construir_reservas_hotel_response",
        new=AsyncMock(return_value=[hotel_resp]),
    ), patch(
        "app.services.reserva_service.obtener_detalles_habitaciones_por_ids",
        new=AsyncMock(return_value={}),
    ):
        response_match = await listar_reservas_hotel_service(
            db=mock_db,
            authorization_header="Bearer token",
            skip=0,
            limit=10,
            tipo_habitacion="suite",
        )

    assert response_match.total == 1

    mock_db.execute = AsyncMock(return_value=list_result)
    with patch(
        "app.services.reserva_service.obtener_habitaciones_hotel",
        new=AsyncMock(return_value=_make_habitaciones()),
    ), patch(
        "app.services.reserva_service.construir_reservas_hotel_response",
        new=AsyncMock(return_value=[hotel_resp]),
    ), patch(
        "app.services.reserva_service.obtener_detalles_habitaciones_por_ids",
        new=AsyncMock(return_value={}),
    ):
        response_no_match = await listar_reservas_hotel_service(
            db=mock_db,
            authorization_header="Bearer token",
            skip=0,
            limit=10,
            tipo_habitacion="deluxe",
        )

    assert response_no_match.total == 0


@pytest.mark.asyncio
async def test_listar_reservas_hotel_service_estado_pago_pending_filter(mock_db):
    """estado_pago=pending keeps reservations with estado_pago=None."""
    reserva = _reserva_modificable()

    list_result = _make_list_result([reserva])
    mock_db.execute = AsyncMock(return_value=list_result)

    hotel_resp = _hotel_reserva_response(reserva)  # estado_pago=None (pago_id is None)
    assert hotel_resp.estado_pago is None

    with patch(
        "app.services.reserva_service.obtener_habitaciones_hotel",
        new=AsyncMock(return_value=_make_habitaciones()),
    ), patch(
        "app.services.reserva_service.construir_reservas_hotel_response",
        new=AsyncMock(return_value=[hotel_resp]),
    ), patch(
        "app.services.reserva_service.obtener_detalles_habitaciones_por_ids",
        new=AsyncMock(return_value={}),
    ):
        response = await listar_reservas_hotel_service(
            db=mock_db,
            authorization_header="Bearer token",
            skip=0,
            limit=10,
            estado_pago=EstadoPagoFiltro.pending,
        )

    assert response.total == 1
    assert len(response.reservas) == 1


@pytest.mark.asyncio
async def test_listar_reservas_hotel_service_estado_pago_successful_filter(mock_db):
    """estado_pago=successful keeps only successful-payment reservations."""
    reserva = _reserva_modificable()

    list_result = _make_list_result([reserva])
    mock_db.execute = AsyncMock(return_value=list_result)

    hotel_resp_pending = _hotel_reserva_response(reserva)  # estado_pago=None

    with patch(
        "app.services.reserva_service.obtener_habitaciones_hotel",
        new=AsyncMock(return_value=_make_habitaciones()),
    ), patch(
        "app.services.reserva_service.construir_reservas_hotel_response",
        new=AsyncMock(return_value=[hotel_resp_pending]),
    ), patch(
        "app.services.reserva_service.obtener_detalles_habitaciones_por_ids",
        new=AsyncMock(return_value={}),
    ):
        response = await listar_reservas_hotel_service(
            db=mock_db,
            authorization_header="Bearer token",
            skip=0,
            limit=10,
            estado_pago=EstadoPagoFiltro.successful,
        )

    assert response.total == 0


@pytest.mark.asyncio
async def test_listar_reservas_hotel_service_in_memory_pagination(mock_db):
    """In-memory filtering applies skip/limit after filtering; total reflects filtered count."""
    now = datetime.now(UTC)
    reservas_db = [
        _reserva_modificable(id=uuid.uuid4(), estado="confirmada")
        for _ in range(5)
    ]

    list_result = _make_list_result(reservas_db)
    mock_db.execute = AsyncMock(return_value=list_result)

    hotel_responses = [_hotel_reserva_response(r) for r in reservas_db]

    with patch(
        "app.services.reserva_service.obtener_habitaciones_hotel",
        new=AsyncMock(return_value=_make_habitaciones()),
    ), patch(
        "app.services.reserva_service.construir_reservas_hotel_response",
        new=AsyncMock(return_value=hotel_responses),
    ), patch(
        "app.services.reserva_service.obtener_detalles_habitaciones_por_ids",
        new=AsyncMock(return_value={}),
    ):
        response = await listar_reservas_hotel_service(
            db=mock_db,
            authorization_header="Bearer token",
            skip=2,
            limit=2,
            nombre_viajero="alice",
        )

    # All 5 match "alice" → total=5, page[2:4] → 2 reservas
    assert response.total == 5
    assert len(response.reservas) == 2


@pytest.mark.asyncio
async def test_listar_reservas_hotel_service_enriches_habitaciones(mock_db):
    """habitaciones list is enriched with nombre_habitacion from room summary."""
    reserva = _reserva_modificable()

    count_result = MagicMock()
    count_result.scalar_one.return_value = 1
    list_result = _make_list_result([reserva])
    mock_db.execute = AsyncMock(side_effect=[count_result, list_result])

    room_detalle = HabitacionReservaDetalleResponse(
        id=HAB_ID,
        nombre_habitacion="Deluxe King Suite",
        nombre_hotel="Grand Palace",
        imagenes_hotel=[],
        numero_habitacion="101",
        monto_habitacion=100,
        impuestos_habitacion=10,
    )

    with patch(
        "app.services.reserva_service.obtener_habitaciones_hotel",
        new=AsyncMock(return_value=_make_habitaciones()),
    ), patch(
        "app.services.reserva_service.construir_reservas_hotel_response",
        new=AsyncMock(return_value=[_hotel_reserva_response(reserva)]),
    ), patch(
        "app.services.reserva_service.obtener_detalles_habitaciones_por_ids",
        new=AsyncMock(return_value={HAB_ID: room_detalle}),
    ):
        response = await listar_reservas_hotel_service(
            db=mock_db,
            authorization_header="Bearer token",
            skip=0,
            limit=10,
        )

    assert len(response.habitaciones) == 1
    assert response.habitaciones[0].nombre_habitacion == "Deluxe King Suite"


# ---------------------------------------------------------------------------
# modificar_reserva_service — pago_id guards
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_modificar_reserva_service_link_pago_success(mock_db):
    """Linking pago_id on a pendiente reservation with no prior payment succeeds."""
    pago_id = uuid.uuid4()
    reserva = _reserva_modificable(estado="pendiente")
    load_result = MagicMock()
    load_result.scalar_one_or_none.return_value = reserva
    no_conflict = MagicMock()
    no_conflict.scalar_one_or_none.return_value = None
    mock_db.execute = AsyncMock(side_effect=[load_result, no_conflict])

    current = User(id=USER_ID, email="viajero@test.com", role=RoleEnum.USER)
    body = ModificarReservaRequest(pago_id=pago_id)

    out = await modificar_reserva_service(
        db=mock_db,
        reserva_id=RESERVA_ID,
        body=body,
        current_user=current,
    )

    assert out.pago_id == pago_id
    assert mock_db.flush.await_count == 1
    assert mock_db.commit.await_count == 1


@pytest.mark.asyncio
async def test_modificar_reserva_service_409_pago_id_on_confirmada(mock_db):
    """Setting pago_id on a confirmada reservation raises 409."""
    reserva = _reserva_modificable(estado="confirmada")
    load_result = MagicMock()
    load_result.scalar_one_or_none.return_value = reserva
    no_conflict = MagicMock()
    no_conflict.scalar_one_or_none.return_value = None
    mock_db.execute = AsyncMock(side_effect=[load_result, no_conflict])

    current = User(id=USER_ID, email="viajero@test.com", role=RoleEnum.USER)
    body = ModificarReservaRequest(pago_id=uuid.uuid4())

    with pytest.raises(HTTPException) as exc:
        await modificar_reserva_service(
            db=mock_db,
            reserva_id=RESERVA_ID,
            body=body,
            current_user=current,
        )

    assert exc.value.status_code == 409
    assert exc.value.detail == "Solo se puede asociar un pago a una reserva pendiente"
    mock_db.commit.assert_not_called()


@pytest.mark.asyncio
async def test_modificar_reserva_service_409_pago_id_already_linked(mock_db):
    """Setting pago_id when a payment is already linked raises 409."""
    existing_pago_id = uuid.uuid4()
    reserva = _reserva_modificable(estado="pendiente")
    reserva.pago_id = existing_pago_id
    load_result = MagicMock()
    load_result.scalar_one_or_none.return_value = reserva
    no_conflict = MagicMock()
    no_conflict.scalar_one_or_none.return_value = None
    mock_db.execute = AsyncMock(side_effect=[load_result, no_conflict])

    current = User(id=USER_ID, email="viajero@test.com", role=RoleEnum.USER)
    body = ModificarReservaRequest(pago_id=uuid.uuid4())

    with pytest.raises(HTTPException) as exc:
        await modificar_reserva_service(
            db=mock_db,
            reserva_id=RESERVA_ID,
            body=body,
            current_user=current,
        )

    assert exc.value.status_code == 409
    assert exc.value.detail == "La reserva ya tiene un pago asociado"
    assert reserva.pago_id == existing_pago_id
    mock_db.commit.assert_not_called()


# ---------------------------------------------------------------------------
# eliminar_reserva_service
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
@pytest.mark.parametrize("estado", ["pendiente", "cancelada"])
async def test_eliminar_reserva_service_success(mock_db, estado):
    """Deleting a pendiente or cancelada reservation owned by the user succeeds."""
    reserva = _build_reserva(estado)
    mock_db.execute = AsyncMock(return_value=_execute_result_with_reserva(reserva))
    mock_db.delete = AsyncMock()
    current = User(id=USER_ID, email="viajero@test.com", role=RoleEnum.USER)

    await eliminar_reserva_service(db=mock_db, reserva_id=reserva.id, current_user=current)

    mock_db.delete.assert_awaited_once_with(reserva)
    assert mock_db.commit.await_count == 1


@pytest.mark.asyncio
async def test_eliminar_reserva_service_404_not_found(mock_db):
    """Deleting a non-existent reservation raises 404."""
    mock_db.execute = AsyncMock(return_value=_execute_result_no_conflict())
    current = User(id=USER_ID, email="viajero@test.com", role=RoleEnum.USER)

    with pytest.raises(HTTPException) as exc:
        await eliminar_reserva_service(
            db=mock_db, reserva_id=uuid.uuid4(), current_user=current
        )

    assert exc.value.status_code == 404
    mock_db.commit.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize("estado", ["confirmada"])
async def test_eliminar_reserva_service_409_active_reservation(mock_db, estado):
    """Deleting a confirmed reservation raises 409."""
    reserva = _build_reserva(estado)
    mock_db.execute = AsyncMock(return_value=_execute_result_with_reserva(reserva))
    mock_db.delete = AsyncMock()
    current = User(id=USER_ID, email="viajero@test.com", role=RoleEnum.USER)

    with pytest.raises(HTTPException) as exc:
        await eliminar_reserva_service(
            db=mock_db, reserva_id=reserva.id, current_user=current
        )

    assert exc.value.status_code == 409
    assert "pendientes o canceladas" in exc.value.detail
    mock_db.delete.assert_not_called()
    mock_db.commit.assert_not_called()
