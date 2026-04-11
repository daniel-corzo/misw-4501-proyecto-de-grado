import uuid

from fastapi import APIRouter, status, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.hotel import (
    AmenidadHotel,
    CrearHotelRequest,
    HotelDetalleResponse,
    ListaHotelesResponse,
    CrearHabitacionRequest,
    HabitacionDetalleResponse,
    ListaHabitacionesResponse,
)
from app.services.hotel_service import (
    OrdenHoteles,
    crear_hotel_service,
    get_hotel_by_user,
    listar_hoteles_service,
    obtener_hotel_service,
)
from app.services.habitacion_service import (
    crear_habitacion_service,
    listar_habitaciones_service,
)
from app.models.hotel import Hotel
from travelhub_common.security import get_current_user, User, RoleChecker, RoleEnum
from typing import Annotated

router = APIRouter(prefix="/hoteles", tags=["hoteles"])


@router.get("", response_model=ListaHotelesResponse, status_code=status.HTTP_200_OK)
async def listar_hoteles(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    orden: OrdenHoteles = Query(default="rating_desc"),
    precio_min: float | None = Query(default=None, ge=0),
    precio_max: float | None = Query(default=None, ge=0),
    rango_50_1000: bool = Query(default=False),
    estrellas: list[int] | None = Query(default=None),
    amenidades_populares: list[AmenidadHotel] | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await listar_hoteles_service(
        db=db,
        limit=limit,
        offset=offset,
        orden=orden,
        precio_min=precio_min,
        precio_max=precio_max,
        rango_50_1000=rango_50_1000,
        estrellas=estrellas,
        amenidades_populares=amenidades_populares,
    )


@router.post(
    "", response_model=HotelDetalleResponse, status_code=status.HTTP_201_CREATED
)
async def crear_hotel(body: CrearHotelRequest, db: AsyncSession = Depends(get_db)):
    return await crear_hotel_service(db=db, body=body)


@router.post(
    "/habitaciones",
    response_model=HabitacionDetalleResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(RoleChecker([RoleEnum.MANAGER, RoleEnum.USER]))
    ],
)
async def crear_habitacion(
    body: CrearHabitacionRequest,
    db: AsyncSession = Depends(get_db),
    current_hotel: Annotated[Hotel, Depends(get_hotel_by_user)] = None
):
    return await crear_habitacion_service(db=db, hotel=current_hotel, body=body)


@router.get(
    "/habitaciones",
    response_model=ListaHabitacionesResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[
        Depends(RoleChecker([RoleEnum.MANAGER, RoleEnum.USER]))
    ],
)
async def listar_habitaciones(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_hotel: Annotated[Hotel, Depends(get_hotel_by_user)] = None
):
    return await listar_habitaciones_service(db=db, hotel=current_hotel, limit=limit, offset=offset)


@router.get(
    "/{hotel_id}", response_model=HotelDetalleResponse, status_code=status.HTTP_200_OK
)
async def obtener_hotel(
    hotel_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await obtener_hotel_service(db=db, hotel_id=hotel_id)
