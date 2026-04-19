import uuid
from unittest.mock import AsyncMock
import pytest
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from app.schemas.hotel import CrearHabitacionRequest
from app.services.habitacion_service import (
    actualizar_habitacion_service,
    crear_habitacion_service,
    listar_habitaciones_service,
)
from app.models.hotel import Hotel
from app.models.habitacion import Habitacion


class MockScalarOneOrNoneResult:
    def __init__(self, value):
        self._value = value

    def scalar_one_or_none(self):
        return self._value


@pytest.fixture
def mock_db_session():
    from unittest.mock import MagicMock
    session = AsyncMock()
    session.add = MagicMock()
    return session

@pytest.mark.asyncio
async def test_crear_habitacion_success(mock_db_session):
    hotel_id = uuid.uuid4()
    body = CrearHabitacionRequest(
        capacidad=2,
        numero="101",
        descripcion="Vista al mar",
        monto=100,
        impuestos=10,
        disponible=True,
        imagenes=[]
    )

    mock_hotel = Hotel(id=hotel_id, nombre="Hotel Test")

    response = await crear_habitacion_service(
        db=mock_db_session, hotel=mock_hotel, body=body
    )

    assert response.numero == body.numero
    assert response.capacidad == body.capacidad
    mock_db_session.execute.assert_not_called()
    mock_db_session.add.assert_called_once()
    mock_db_session.commit.assert_called_once()
    mock_db_session.refresh.assert_called_once()

@pytest.mark.asyncio
async def test_crear_habitacion_hotel_not_found(mock_db_session):
    hotel_id = uuid.uuid4()
    body = CrearHabitacionRequest(
        capacidad=2,
        numero="101",
        descripcion="Vista al mar",
        monto=100,
        impuestos=10,
        disponible=True,
        imagenes=[]
    )

    with pytest.raises(HTTPException) as exc_info:
        await crear_habitacion_service(db=mock_db_session, hotel=None, body=body)
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Hotel no encontrado"
    mock_db_session.execute.assert_not_called()


@pytest.mark.asyncio
async def test_crear_habitacion_duplicate_numero_conflict(mock_db_session):
    hotel_id = uuid.uuid4()
    body = CrearHabitacionRequest(
        capacidad=2,
        numero="101",
        descripcion="Vista al mar",
        monto=100,
        impuestos=10,
        disponible=True,
        imagenes=[],
    )
    mock_hotel = Hotel(id=hotel_id, nombre="Hotel Test")

    class FakeOrig:
        constraint_name = "uq_habitacion_hotel_numero"

    mock_db_session.commit.side_effect = IntegrityError(None, None, FakeOrig())

    with pytest.raises(HTTPException) as exc_info:
        await crear_habitacion_service(db=mock_db_session, hotel=mock_hotel, body=body)

    assert exc_info.value.status_code == 409
    assert (
        exc_info.value.detail == "Ya existe una habitación con ese número en este hotel"
    )
    mock_db_session.execute.assert_not_called()
    mock_db_session.add.assert_called_once()
    mock_db_session.commit.assert_awaited_once()
    mock_db_session.rollback.assert_awaited_once()
    mock_db_session.refresh.assert_not_called()


@pytest.mark.asyncio
async def test_crear_habitacion_integrity_error_other_reraises(mock_db_session):
    hotel_id = uuid.uuid4()
    body = CrearHabitacionRequest(
        capacidad=2,
        numero="101",
        descripcion="Vista al mar",
        monto=100,
        impuestos=10,
        disponible=True,
        imagenes=[],
    )
    mock_hotel = Hotel(id=hotel_id, nombre="Hotel Test")

    class FakeOrig:
        constraint_name = "other_constraint"

    mock_db_session.commit.side_effect = IntegrityError(None, None, FakeOrig())

    with pytest.raises(IntegrityError):
        await crear_habitacion_service(db=mock_db_session, hotel=mock_hotel, body=body)

    mock_db_session.execute.assert_not_called()
    mock_db_session.rollback.assert_awaited_once()
    mock_db_session.refresh.assert_not_called()


@pytest.mark.asyncio
async def test_actualizar_habitacion_success(mock_db_session):
    hotel_id = uuid.uuid4()
    habitacion_id = uuid.uuid4()
    body = CrearHabitacionRequest(
        capacidad=3,
        numero="202",
        descripcion="Suite remodelada",
        monto=220,
        impuestos=22,
        disponible=True,
        imagenes=["https://example.com/habitacion.jpg"],
    )

    mock_hotel = Hotel(id=hotel_id, nombre="Hotel Test")
    existing_room = Habitacion(
        id=habitacion_id,
        capacidad=2,
        numero="101",
        descripcion="Vista al mar",
        monto=100,
        impuestos=10,
        disponible=False,
        imagenes=[],
        hotel_id=hotel_id,
    )
    mock_db_session.execute = AsyncMock(
        side_effect=[
            MockScalarOneOrNoneResult(existing_room),
            MockScalarOneOrNoneResult(None),
        ]
    )

    response = await actualizar_habitacion_service(
        db=mock_db_session,
        hotel=mock_hotel,
        habitacion_id=habitacion_id,
        body=body,
    )

    assert response.id == habitacion_id
    assert response.numero == body.numero
    assert response.capacidad == body.capacidad
    assert response.monto == body.monto
    assert response.impuestos == body.impuestos
    assert response.descripcion == body.descripcion
    assert response.imagenes == body.imagenes
    assert response.disponible is True
    mock_db_session.add.assert_not_called()
    assert mock_db_session.execute.await_count == 2
    mock_db_session.commit.assert_awaited_once()
    mock_db_session.refresh.assert_awaited_once_with(existing_room)


@pytest.mark.asyncio
async def test_actualizar_habitacion_not_found(mock_db_session):
    hotel_id = uuid.uuid4()
    habitacion_id = uuid.uuid4()
    body = CrearHabitacionRequest(
        capacidad=3,
        numero="202",
        descripcion="Suite remodelada",
        monto=220,
        impuestos=22,
        disponible=True,
        imagenes=[],
    )

    mock_hotel = Hotel(id=hotel_id, nombre="Hotel Test")
    mock_db_session.execute = AsyncMock(return_value=MockScalarOneOrNoneResult(None))

    with pytest.raises(HTTPException) as exc_info:
        await actualizar_habitacion_service(
            db=mock_db_session,
            hotel=mock_hotel,
            habitacion_id=habitacion_id,
            body=body,
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Habitación no encontrada"
    mock_db_session.add.assert_not_called()
    mock_db_session.commit.assert_not_called()
    mock_db_session.refresh.assert_not_called()


@pytest.mark.asyncio
async def test_actualizar_habitacion_duplicate_numero_conflict(mock_db_session):
    hotel_id = uuid.uuid4()
    habitacion_id = uuid.uuid4()
    body = CrearHabitacionRequest(
        capacidad=3,
        numero="202",
        descripcion="Suite remodelada",
        monto=220,
        impuestos=22,
        disponible=True,
        imagenes=[],
    )

    mock_hotel = Hotel(id=hotel_id, nombre="Hotel Test")
    existing_room = Habitacion(
        id=habitacion_id,
        capacidad=2,
        numero="101",
        descripcion="Vista al mar",
        monto=100,
        impuestos=10,
        disponible=True,
        imagenes=[],
        hotel_id=hotel_id,
    )

    mock_db_session.execute = AsyncMock(
        side_effect=[
            MockScalarOneOrNoneResult(existing_room),
            MockScalarOneOrNoneResult(uuid.uuid4()),
        ]
    )

    with pytest.raises(HTTPException) as exc_info:
        await actualizar_habitacion_service(
            db=mock_db_session,
            hotel=mock_hotel,
            habitacion_id=habitacion_id,
            body=body,
        )

    assert exc_info.value.status_code == 409
    assert (
        exc_info.value.detail == "Ya existe una habitación con ese número en este hotel"
    )
    mock_db_session.add.assert_not_called()
    assert mock_db_session.execute.await_count == 2
    mock_db_session.commit.assert_not_called()
    mock_db_session.rollback.assert_not_called()
    mock_db_session.refresh.assert_not_called()


@pytest.mark.asyncio
async def test_listar_habitaciones_success(mock_db_session):
    hotel_id = uuid.uuid4()
    mock_hotel = Hotel(id=hotel_id, nombre="Hotel Test")
    
    class MockResultCount:
        def scalar(self):
            return 2

    class MockResultQuery:
        def scalars(self):
            class MockScalars:
                def all(self):
                    return [
                        Habitacion(
                            id=uuid.uuid4(),
                            capacidad=2,
                            numero="101",
                            descripcion="Vista al mar",
                            monto=100,
                            impuestos=10,
                            disponible=True,
                            imagenes=[],
                            hotel_id=hotel_id
                        ),
                        Habitacion(
                            id=uuid.uuid4(),
                            capacidad=4,
                            numero="102",
                            descripcion="Vista a la montaña",
                            monto=150,
                            impuestos=15,
                            disponible=True,
                            imagenes=[],
                            hotel_id=hotel_id
                        )
                    ]
            return MockScalars()
            
    mock_db_session.execute.side_effect = [MockResultCount(), MockResultQuery()]
    
    response = await listar_habitaciones_service(db=mock_db_session, hotel=mock_hotel)
    
    assert response.total == 2
    assert len(response.habitaciones) == 2
    assert response.habitaciones[0].numero == "101"
    assert response.habitaciones[1].numero == "102"
