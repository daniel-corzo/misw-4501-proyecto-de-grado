import uuid

from fastapi import APIRouter, status, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.hotel import CrearHotelRequest, HotelDetalleResponse, ListaHotelesResponse
from app.services.hotel_service import (
    AmenidadPopular,
    OrdenHoteles,
    crear_hotel_service,
    listar_hoteles_service,
    obtener_hotel_service,
)
from travelhub_common.security import get_current_user, User, RoleChecker, RoleEnum

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
    amenidades_populares: list[AmenidadPopular] | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
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


@router.get("/{hotel_id}", response_model=HotelDetalleResponse, status_code=status.HTTP_200_OK)
async def obtener_hotel(
    hotel_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await obtener_hotel_service(db=db, hotel_id=hotel_id)


@router.post("", response_model=HotelDetalleResponse, status_code=status.HTTP_201_CREATED)
async def crear_hotel(
    body: CrearHotelRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleChecker([RoleEnum.ADMIN, RoleEnum.MANAGER]))
):
    return await crear_hotel_service(db=db, body=body)
