import uuid
from datetime import date, datetime, UTC
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException

from app.schemas.reserva import CrearReservaRequest
from app.services.reserva_service import crear_reserva_service
from travelhub_common.security import RoleEnum, User

USER_ID = uuid.uuid4()
HAB_ID = uuid.uuid4()


def _execute_result_no_conflict():
    r = MagicMock()
    r.scalar_one_or_none.return_value = None
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
