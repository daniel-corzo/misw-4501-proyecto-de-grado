import uuid
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.habitacion import Habitacion
from app.models.hotel import Hotel
from app.schemas.hotel import (
    CrearHabitacionRequest,
    HabitacionDetalleResponse,
    ListaHabitacionesResponse,
)


async def crear_habitacion_service(
    db: AsyncSession, hotel: Hotel, body: CrearHabitacionRequest
) -> HabitacionDetalleResponse:
    # Validate if hotel exists
    if not hotel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Hotel no encontrado"
        )

    dup_result = await db.execute(
        select(Habitacion)
        .where(
            Habitacion.hotel_id == hotel.id,
            Habitacion.numero == body.numero,
        )
        .limit(1)
    )
    if dup_result.scalars().first() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe una habitación con ese número en este hotel",
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
    await db.commit()
    await db.refresh(habitacion)

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
            HabitacionDetalleResponse(
                id=h.id,
                capacidad=h.capacidad,
                numero=h.numero,
                descripcion=h.descripcion,
                imagenes=h.imagenes or [],
                monto=h.monto,
                impuestos=h.impuestos,
                disponible=h.disponible,
            )
            for h in habitaciones
        ]
    )
