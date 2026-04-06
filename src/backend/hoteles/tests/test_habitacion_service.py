import uuid
from unittest.mock import AsyncMock, patch
import pytest
from fastapi import HTTPException
from sqlalchemy.orm import selectinload

from app.schemas.hotel import CrearHabitacionRequest
from app.services.habitacion_service import crear_habitacion_service, listar_habitaciones_service
from app.models.hotel import Hotel
from app.models.habitacion import Habitacion

class _ScalarResult:
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
    mock_db_session.execute.return_value = _ScalarResult(mock_hotel)
    
    with patch("app.services.habitacion_service.Habitacion", autospec=True) as MockHabitacion:
        mock_habitacion_instance = MockHabitacion.return_value
        mock_habitacion_instance.id = uuid.uuid4()
        mock_habitacion_instance.numero = body.numero
        mock_habitacion_instance.capacidad = body.capacidad
        mock_habitacion_instance.descripcion = body.descripcion
        mock_habitacion_instance.monto = body.monto
        mock_habitacion_instance.impuestos = body.impuestos
        mock_habitacion_instance.disponible = body.disponible
        mock_habitacion_instance.imagenes = body.imagenes

        response = await crear_habitacion_service(db=mock_db_session, hotel=mock_hotel, body=body)

        assert response.numero == body.numero
        assert response.capacidad == body.capacidad
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
    
    mock_db_session.execute.return_value = _ScalarResult(None)

    with pytest.raises(HTTPException) as exc_info:
        await crear_habitacion_service(db=mock_db_session, hotel=None, body=body)
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Hotel no encontrado"

@pytest.mark.asyncio
async def test_listar_habitaciones_success(mock_db_session):
    hotel_id = uuid.uuid4()
    mock_hotel = Hotel(id=hotel_id, nombre="Hotel Test")
    
    mock_db_session.execute.return_value = _ScalarResult(mock_hotel)
    
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
