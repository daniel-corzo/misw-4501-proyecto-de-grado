import uuid
from fastapi import HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.habitacion import Habitacion
from app.models.hotel import Hotel
from app.schemas.hotel import (
    CrearHabitacionRequest,
    HabitacionDetalleResponse,
    ListaHabitacionesResponse,
)

_HABITACION_NUMERO_UQ = "uq_habitacion_hotel_numero"


def _is_duplicate_habitacion_numero_error(exc: IntegrityError) -> bool:
    orig = exc.orig
    if orig is not None:
        if getattr(orig, "constraint_name", None) == _HABITACION_NUMERO_UQ:
            return True
        if _HABITACION_NUMERO_UQ in str(orig):
            return True
    return _HABITACION_NUMERO_UQ in str(exc)


def _build_habitacion_response(habitacion: Habitacion) -> HabitacionDetalleResponse:
    return HabitacionDetalleResponse(
        id=habitacion.id,
        capacidad=habitacion.capacidad,
        numero=habitacion.numero,
        descripcion=habitacion.descripcion,
        imagenes=habitacion.imagenes or [],
        monto=habitacion.monto,
        impuestos=habitacion.impuestos,
        disponible=habitacion.disponible,
    )


async def crear_habitacion_service(
    db: AsyncSession, hotel: Hotel, body: CrearHabitacionRequest
) -> HabitacionDetalleResponse:
    # Validate if hotel exists
    if not hotel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Hotel no encontrado"
        )

    habitacion = Habitacion(
        id=uuid.uuid4(),
        capacidad=body.capacidad,
        numero=body.numero,
        descripcion=body.descripcion,
        imagenes=body.imagenes,
        monto=body.monto,
        impuestos=body.impuestos,
        disponible=body.disponible,
        hotel_id=hotel.id,
    )

    db.add(habitacion)
    try:
        await db.commit()
        await db.refresh(habitacion)
    except IntegrityError as exc:
        await db.rollback()
        if _is_duplicate_habitacion_numero_error(exc):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe una habitación con ese número en este hotel",
            ) from None
        raise

    return _build_habitacion_response(habitacion)


async def actualizar_habitacion_service(
    db: AsyncSession,
    hotel: Hotel,
    habitacion_id: uuid.UUID,
    body: CrearHabitacionRequest,
) -> HabitacionDetalleResponse:
    if not hotel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Hotel no encontrado"
        )

    result = await db.execute(
        select(Habitacion).where(
            Habitacion.id == habitacion_id,
            Habitacion.hotel_id == hotel.id,
        )
    )
    habitacion = result.scalar_one_or_none()

    if habitacion is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Habitación no encontrada",
        )

    duplicate_result = await db.execute(
        select(Habitacion.id).where(
            Habitacion.hotel_id == hotel.id,
            Habitacion.numero == body.numero,
            Habitacion.id != habitacion_id,
        )
    )
    duplicate_habitacion_id = duplicate_result.scalar_one_or_none()
    if duplicate_habitacion_id is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe una habitación con ese número en este hotel",
        )

    habitacion.capacidad = body.capacidad
    habitacion.numero = body.numero
    habitacion.descripcion = body.descripcion
    habitacion.imagenes = body.imagenes
    habitacion.monto = body.monto
    habitacion.impuestos = body.impuestos
    habitacion.disponible = body.disponible

    try:
        await db.commit()
        await db.refresh(habitacion)
    except IntegrityError as exc:
        await db.rollback()
        if _is_duplicate_habitacion_numero_error(exc):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe una habitación con ese número en este hotel",
            ) from None
        raise

    return _build_habitacion_response(habitacion)


async def listar_habitaciones_service(
    db: AsyncSession, hotel: Hotel, limit: int = 20, offset: int = 0
) -> ListaHabitacionesResponse:
    if not hotel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Hotel no encontrado"
        )
    total_result = await db.execute(
        select(func.count())
        .select_from(Habitacion)
        .where(Habitacion.hotel_id == hotel.id)
    )
    total = total_result.scalar() or 0

    result = await db.execute(
        select(Habitacion)
        .where(Habitacion.hotel_id == hotel.id)
        .order_by(Habitacion.numero)
        .limit(limit)
        .offset(offset)
    )
    habitaciones = result.scalars().all()

    return ListaHabitacionesResponse(
        total=total,
        habitaciones=[
            _build_habitacion_response(h)
            for h in habitaciones
        ]
    )
