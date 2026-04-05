import uuid
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.habitacion import Habitacion
from app.models.hotel import Hotel
from app.schemas.hotel import CrearHabitacionRequest, HabitacionDetalleResponse

async def crear_habitacion_service(
    db: AsyncSession, 
    hotel: Hotel, 
    body: CrearHabitacionRequest
) -> HabitacionDetalleResponse:
    # Validate if hotel exists
    if not hotel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hotel no encontrado"
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
        hotel_id=hotel.id
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
        disponible=habitacion.disponible
    )

async def listar_habitaciones_service(
    db: AsyncSession,
    hotel: Hotel
) -> list[HabitacionDetalleResponse]:
    if not hotel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hotel no encontrado"
        )
    
    result = await db.execute(
        select(Habitacion).where(Habitacion.hotel_id == hotel.id)
    )
    habitaciones = result.scalars().all()
    
    return [
        HabitacionDetalleResponse(
            id=h.id,
            capacidad=h.capacidad,
            numero=h.numero,
            descripcion=h.descripcion,
            imagenes=h.imagenes or [],
            monto=h.monto,
            impuestos=h.impuestos,
            disponible=h.disponible
        )
        for h in habitaciones
    ]

