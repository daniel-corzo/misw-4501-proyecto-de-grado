import uuid
from datetime import date, datetime, UTC
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException

from app.models.reserva import Reserva
from app.schemas.reserva import CrearReservaRequest
from app.services.reserva_service import cancelar_reserva_service, crear_reserva_service, listar_reservas_usuario_service
from travelhub_common.security import RoleEnum, User

USER_ID = uuid.uuid4()
OTHER_ID = uuid.uuid4()
HAB_ID = uuid.uuid4()


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
    
    response = await listar_reservas_usuario_service(db=mock_db, usuario_id=USER_ID, skip=0, limit=10, current_user=current)
    
    assert response.total == 1
    assert len(response.reservas) == 1
    assert response.reservas[0].id == mock_reserva.id

@pytest.mark.asyncio
async def test_listar_reservas_usuario_forbidden(mock_db):
    current = User(id=USER_ID, email="user@test.com", role=RoleEnum.USER)
    
    with pytest.raises(HTTPException) as exc:
        await listar_reservas_usuario_service(db=mock_db, usuario_id=OTHER_ID, skip=0, limit=10, current_user=current)
    
    assert exc.value.status_code == 403
