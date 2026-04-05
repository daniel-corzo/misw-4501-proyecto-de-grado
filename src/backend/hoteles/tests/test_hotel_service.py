import uuid
from datetime import datetime, UTC, time
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException

from app.schemas.hotel import AmenidadHotel, CrearHotelRequest
from app.services.hotel_service import (
    crear_hotel_service,
    listar_hoteles_service,
    obtener_hotel_service,
)


class _ScalarResult:
    def __init__(self, value):
        self._value = value

    def scalar_one(self):
        return self._value

    def scalar_one_or_none(self):
        return self._value


class _RowsResult:
    def __init__(self, rows):
        self._rows = rows

    def all(self):
        return self._rows


@pytest.mark.anyio
async def test_listar_hoteles_service_returns_filtered_result():
    hotel_id = uuid.uuid4()
    created_at = datetime.now(UTC)
    hotel = SimpleNamespace(
        id=hotel_id,
        nombre="Hotel Prueba",
        ciudad="Bogota",
        pais="Colombia",
        estrellas=4,
        imagenes=["img1.jpg", "img2.jpg"],
        created_at=created_at,
    )

    db = AsyncMock()
    db.execute = AsyncMock(
        side_effect=[
            _ScalarResult(1),
            _RowsResult([(hotel, 120)]),
        ]
    )

    response = await listar_hoteles_service(
        db=db,
        limit=20,
        offset=0,
        orden="precio_asc",
        precio_min=50,
        precio_max=1000,
        rango_50_1000=True,
        estrellas=[3, 4, 4],
        amenidades_populares=[AmenidadHotel.WIFI, AmenidadHotel.POOL],
    )

    assert response.total == 1
    assert len(response.hoteles) == 1
    assert response.hoteles[0].id == hotel_id
    assert response.hoteles[0].nombre == "Hotel Prueba"
    assert response.hoteles[0].estrellas == 4
    assert response.hoteles[0].imagenes == ["img1.jpg", "img2.jpg"]
    assert response.hoteles[0].precio_minimo == 120
    assert db.execute.await_count == 2


@pytest.mark.anyio
async def test_listar_hoteles_service_raises_on_invalid_price_range():
    db = AsyncMock()
    db.execute = AsyncMock()

    with pytest.raises(HTTPException) as exc:
        await listar_hoteles_service(
            db=db,
            limit=10,
            offset=0,
            orden="rating_desc",
            precio_min=1500,
            precio_max=100,
            rango_50_1000=False,
            estrellas=[5],
            amenidades_populares=None,
        )

    assert exc.value.status_code == 400
    assert "precio_min" in exc.value.detail
    db.execute.assert_not_awaited()


@pytest.mark.anyio
async def test_listar_hoteles_service_raises_when_amenidad_no_es_popular():
    db = AsyncMock()
    db.execute = AsyncMock()

    with pytest.raises(HTTPException) as exc:
        await listar_hoteles_service(
            db=db,
            limit=10,
            offset=0,
            orden="rating_desc",
            precio_min=None,
            precio_max=None,
            rango_50_1000=False,
            estrellas=None,
            amenidades_populares=[AmenidadHotel.GYM],
        )

    assert exc.value.status_code == 400
    assert "amenidades populares" in exc.value.detail
    db.execute.assert_not_awaited()


@pytest.mark.anyio
async def test_obtener_hotel_service_returns_hotel_detail_response():
    hotel_id = uuid.uuid4()
    usuario_id = uuid.uuid4()

    politica = SimpleNamespace(
        id=uuid.uuid4(),
        nombre="Cancelacion",
        descripcion="Sin costo 24h antes",
        tipo="cancelacion",
        penalizacion=0,
        dias_antelacion=1,
    )
    habitacion = SimpleNamespace(
        id=uuid.uuid4(),
        capacidad=2,
        numero="101",
        descripcion="Vista al mar",
        imagenes=["hab1.jpg"],
        monto=300,
        impuestos=57,
        disponible=True,
    )
    hotel = SimpleNamespace(
        id=hotel_id,
        nombre="Hotel Prueba",
        direccion="Calle 1",
        pais="Colombia",
        estado="Cundinamarca",
        departamento="Cundinamarca",
        ciudad="Bogota",
        descripcion="Descripcion",
        amenidades=["WIFI", "POOL"],
        estrellas=4,
        ranking=4.7,
        contacto_celular="3000000000",
        contacto_email="test@hotel.com",
        imagenes=["hotel.jpg"],
        check_in=datetime.now(UTC).time(),
        check_out=datetime.now(UTC).time(),
        valor_minimo_modificacion=100.0,
        usuario_id=usuario_id,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
        politicas=[politica],
        habitaciones=[habitacion],
    )

    db = AsyncMock()
    db.execute = AsyncMock(return_value=_ScalarResult(hotel))

    response = await obtener_hotel_service(db=db, hotel_id=hotel_id)

    assert response.id == hotel_id
    assert response.nombre == "Hotel Prueba"
    assert response.pais == "Colombia"
    assert len(response.politicas) == 1
    assert len(response.habitaciones) == 1
    assert response.habitaciones[0].monto == 300


@pytest.mark.anyio
async def test_obtener_hotel_service_raises_404_when_not_found():
    db = AsyncMock()
    db.execute = AsyncMock(return_value=_ScalarResult(None))

    with pytest.raises(HTTPException) as exc:
        await obtener_hotel_service(db=db, hotel_id=uuid.uuid4())

    assert exc.value.status_code == 404


@pytest.mark.anyio
@patch("app.services.hotel_service.httpx.AsyncClient")
async def test_crear_hotel_service_returns_created_hotel_response(mock_async_client):
    mock_response = MagicMock()
    mock_response.status_code = 201
    mock_response.json.return_value = {"id": str(uuid.uuid4())}
    mock_client_instance = AsyncMock()
    mock_client_instance.post.return_value = mock_response
    mock_client_instance.__aenter__.return_value = mock_client_instance
    mock_async_client.return_value = mock_client_instance

    usuario_id = uuid.uuid4()
    body = CrearHotelRequest(
        nombre="Hotel Nuevo",
        direccion="Calle 10",
        pais="Colombia",
        estado="Cundinamarca",
        departamento="Cundinamarca",
        ciudad="Medellin",
        descripcion="Test",
        amenidades=[],
        estrellas=5,
        ranking=4.6,
        contacto_celular="3000000000",
        contacto_email="hotel@nuevo.com",
        email="hotel@nuevo.com",
        password="secretpassword",
        imagenes=["hotel1.jpg"],
        check_in=time(15, 0),
        check_out=time(12, 0),
        valor_minimo_modificacion=100.0,
        usuario_id=usuario_id,
        politicas=[
            {
                "nombre": "Cancelacion flexible",
                "descripcion": "Gratis hasta 24h",
                "tipo": "cancelacion",
                "penalizacion": 0,
                "dias_antelacion": 1,
            }
        ],
        habitaciones=[
            {
                "capacidad": 2,
                "numero": "101",
                "descripcion": "Vista ciudad",
                "imagenes": ["h1.jpg"],
                "monto": 250,
                "impuestos": 45,
                "disponible": True,
            }
        ],
    )

    hotel_id = uuid.uuid4()
    created_at = datetime.now(UTC)
    updated_at = datetime.now(UTC)
    politica = SimpleNamespace(
        id=uuid.uuid4(),
        nombre="Cancelacion flexible",
        descripcion="Gratis hasta 24h",
        tipo="cancelacion",
        penalizacion=0,
        dias_antelacion=1,
    )
    habitacion = SimpleNamespace(
        id=uuid.uuid4(),
        capacidad=2,
        numero="101",
        descripcion="Vista ciudad",
        imagenes=["h1.jpg"],
        monto=250,
        impuestos=45,
        disponible=True,
    )
    hotel = SimpleNamespace(
        id=hotel_id,
        nombre=body.nombre,
        direccion=body.direccion,
        pais=body.pais,
        estado=body.estado,
        departamento=body.departamento,
        ciudad=body.ciudad,
        descripcion=body.descripcion,
        amenidades=[],
        estrellas=body.estrellas,
        ranking=body.ranking,
        contacto_celular=body.contacto_celular,
        contacto_email=body.contacto_email,
        imagenes=body.imagenes,
        check_in=body.check_in,
        check_out=body.check_out,
        valor_minimo_modificacion=body.valor_minimo_modificacion,
        usuario_id=body.usuario_id,
        created_at=created_at,
        updated_at=updated_at,
        politicas=[politica],
        habitaciones=[habitacion],
    )

    db = AsyncMock()
    db.add = MagicMock()
    db.execute = AsyncMock(return_value=_ScalarResult(hotel))

    response = await crear_hotel_service(db=db, body=body)

    assert response.id is not None
    assert response.nombre == body.nombre
    assert response.ciudad == body.ciudad
    assert response.pais == body.pais
    assert response.estrellas == 5
    assert len(response.politicas) == 1
    assert len(response.habitaciones) == 1
    db.flush.assert_awaited_once()
    db.commit.assert_awaited_once()


@pytest.mark.anyio
@patch("app.services.hotel_service.httpx.AsyncClient")
async def test_crear_hotel_service_raises_400_on_user_creation_error(mock_async_client):
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.json.return_value = {"detail": "El email ya existe"}
    mock_client_instance = AsyncMock()
    mock_client_instance.post.return_value = mock_response
    mock_client_instance.__aenter__.return_value = mock_client_instance
    mock_async_client.return_value = mock_client_instance

    body = CrearHotelRequest(
        nombre="Hotel",
        direccion="Calle 10",
        pais="Colombia",
        estado="Cundinamarca",
        departamento="Cundinamarca",
        ciudad="Medellin",
        amenidades=[],
        estrellas=5,
        ranking=4.6,
        email="duplicado@hotel.com",
        password="pass",
        check_in=time(15, 0),
        check_out=time(12, 0),
        valor_minimo_modificacion=100.0,
    )
    db = AsyncMock()

    with pytest.raises(HTTPException) as exc:
        await crear_hotel_service(db=db, body=body)

    assert exc.value.status_code == 400
    assert exc.value.detail == "El email ya existe"


@pytest.mark.anyio
@patch("app.services.hotel_service.httpx.AsyncClient")
async def test_crear_hotel_service_raises_500_on_unknown_user_creation_error(mock_async_client):
    mock_response = MagicMock()
    mock_response.status_code = 502
    mock_response.json.side_effect = ValueError("Not JSON")
    mock_client_instance = AsyncMock()
    mock_client_instance.post.return_value = mock_response
    mock_client_instance.__aenter__.return_value = mock_client_instance
    mock_async_client.return_value = mock_client_instance

    body = CrearHotelRequest(
        nombre="Hotel",
        direccion="Calle 10",
        pais="Colombia",
        estado="Cundinamarca",
        departamento="Cundinamarca",
        ciudad="Medellin",
        amenidades=[],
        estrellas=5,
        ranking=4.6,
        email="error@hotel.com",
        password="pass",
        check_in=time(15, 0),
        check_out=time(12, 0),
        valor_minimo_modificacion=100.0,
    )
    db = AsyncMock()

    with pytest.raises(HTTPException) as exc:
        await crear_hotel_service(db=db, body=body)

    assert exc.value.status_code == 500
    assert "Error al crear el usuario para el hotel" in exc.value.detail
