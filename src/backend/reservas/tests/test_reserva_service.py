import os
import uuid
from datetime import date, datetime, UTC
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException

os.environ.setdefault("ENVIRONMENT", "test")

from app.schemas.reserva import CrearReservaRequest
from app.services.reserva_service import crear_reserva_service
from travelhub_common.security import RoleEnum, User

USER_ID = uuid.uuid4()
HAB_ID = uuid.uuid4()
OTHER_ID = uuid.uuid4()


@pytest.fixture
def mock_db():
    session = AsyncMock()
    session.add = MagicMock()

    async def mock_refresh(instance, attribute_names=None):
        if getattr(instance, "created_at", None) is None:
            instance.created_at = datetime.now(UTC)

    session.refresh = AsyncMock(side_effect=mock_refresh)
    session.flush = AsyncMock()
    session.commit = AsyncMock()
    return session


@pytest.mark.asyncio
async def test_crear_reserva_service_forbidden_non_admin(mock_db):
    body = CrearReservaRequest(
        usuario_id=OTHER_ID,
        habitacion_id=HAB_ID,
        fecha_entrada=date(2026, 6, 1),
        fecha_salida=date(2026, 6, 4),
        num_huespedes=1,
    )
    current = User(id=USER_ID, email="a@b.com", role=RoleEnum.USER)

    with pytest.raises(HTTPException) as exc:
        await crear_reserva_service(db=mock_db, body=body, current_user=current)

    assert exc.value.status_code == 403
    mock_db.add.assert_not_called()


@pytest.mark.asyncio
async def test_crear_reserva_service_admin_can_create_for_other(mock_db):
    body = CrearReservaRequest(
        usuario_id=OTHER_ID,
        habitacion_id=HAB_ID,
        fecha_entrada=date(2026, 6, 1),
        fecha_salida=date(2026, 6, 4),
        num_huespedes=1,
    )
    current = User(id=USER_ID, email="admin@test.com", role=RoleEnum.ADMIN)

    out = await crear_reserva_service(db=mock_db, body=body, current_user=current)

    assert out.usuario_id == OTHER_ID
    assert out.habitacion_id == HAB_ID
    assert out.estado.value == "pendiente"
    mock_db.add.assert_called_once()
    assert mock_db.flush.await_count == 1
    assert mock_db.commit.await_count == 1
