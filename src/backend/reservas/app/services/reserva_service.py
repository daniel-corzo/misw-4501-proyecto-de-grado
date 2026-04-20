import uuid
from datetime import date, datetime, time, timezone

from fastapi import HTTPException, status
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from travelhub_common.security import User

from app.models.reserva import Reserva
from app.schemas.reserva import (
    CrearReservaRequest,
    EstadoReserva,
    HabitacionReservaDetalleResponse,
    ReservaDetalleResponse,
    ReservaHabitacionDetalleCompletoResponse,
    ReservaHotelDetalleResponse,
    ReservaResponse,
)


def _fecha_to_utc_start(d: date) -> datetime:
    return datetime.combine(d, time.min, tzinfo=timezone.utc)


def reserva_to_response(
    reserva: Reserva,
    nombre_habitacion: str | None = None,
    nombre_hotel: str | None = None,
    imagenes_hotel: list[str] | None = None,
) -> ReservaResponse:
    habitacion_id = reserva.habitaciones_ids[0] if reserva.habitaciones_ids else None
    if habitacion_id is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Reserva sin habitaciones asociadas",
        )
    return ReservaResponse(
        id=reserva.id,
        habitacion_id=habitacion_id,
        nombre_habitacion=nombre_habitacion,
        nombre_hotel=nombre_hotel,
        imagenes_hotel=imagenes_hotel or [],
        fecha_entrada=reserva.check_in.date(),
        fecha_salida=reserva.check_out.date(),
        num_huespedes=reserva.personas,
        estado=EstadoReserva(reserva.estado),
        pago_id=reserva.pago_id,
        created_at=reserva.created_at,
    )


def reserva_to_detalle_response(
    reserva: Reserva,
    detalle_habitacion: HabitacionReservaDetalleResponse,
) -> ReservaDetalleResponse:
    habitacion_id = reserva.habitaciones_ids[0] if reserva.habitaciones_ids else None
    if habitacion_id is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Reserva sin habitaciones asociadas",
        )

    return ReservaDetalleResponse(
        id=reserva.id,
        codigo_reserva=f"TH-{str(reserva.id).split('-')[0].upper()}",
        estado=EstadoReserva(reserva.estado),
        fecha_entrada=reserva.check_in.date(),
        fecha_salida=reserva.check_out.date(),
        num_huespedes=reserva.personas,
        pago_id=reserva.pago_id,
        created_at=reserva.created_at,
        hotel=ReservaHotelDetalleResponse(
            id=detalle_habitacion.hotel_id,
            nombre=detalle_habitacion.nombre_hotel,
            direccion=detalle_habitacion.direccion_hotel,
            ciudad=detalle_habitacion.ciudad_hotel,
            pais=detalle_habitacion.pais_hotel,
            estrellas=detalle_habitacion.estrellas_hotel,
            ranking=detalle_habitacion.ranking_hotel,
            imagenes=detalle_habitacion.imagenes_hotel,
            contacto_celular=detalle_habitacion.contacto_celular_hotel,
            contacto_email=detalle_habitacion.contacto_email_hotel,
            check_in=detalle_habitacion.check_in_hotel,
            check_out=detalle_habitacion.check_out_hotel,
        ),
        habitacion=ReservaHabitacionDetalleCompletoResponse(
            id=habitacion_id,
            nombre=detalle_habitacion.nombre_habitacion,
            descripcion=detalle_habitacion.descripcion_habitacion,
            numero=detalle_habitacion.numero_habitacion,
            capacidad=detalle_habitacion.capacidad_habitacion,
            imagenes=detalle_habitacion.imagenes_habitacion,
            monto=detalle_habitacion.monto_habitacion,
            impuestos=detalle_habitacion.impuestos_habitacion,
        ),
        amenidades_hotel=detalle_habitacion.amenidades_hotel,
    )


async def crear_reserva_service(
    db: AsyncSession,
    body: CrearReservaRequest,
    current_user: User,
) -> ReservaResponse:
    check_in = _fecha_to_utc_start(body.fecha_entrada)
    check_out = _fecha_to_utc_start(body.fecha_salida)

    conflict_stmt = (
        select(Reserva.id)
        .where(
            and_(
                Reserva.habitaciones_ids.contains([body.habitacion_id]),
                Reserva.check_in < check_out,
                Reserva.check_out > check_in,
                Reserva.estado.in_(
                    [EstadoReserva.pendiente.value, EstadoReserva.confirmada.value]
                ),
            )
        )
        .limit(1)
    )
    conflict = await db.execute(conflict_stmt)
    if conflict.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="La habitación ya tiene una reserva activa en las fechas solicitadas",
        )

    reserva = Reserva(
        id=uuid.uuid4(),
        check_in=check_in,
        check_out=check_out,
        estado=EstadoReserva.pendiente.value,
        personas=body.num_huespedes,
        viajero_id=current_user.id,
        habitaciones_ids=[body.habitacion_id],
        pago_id=body.pago_id,
    )
    db.add(reserva)
    await db.flush()
    await db.commit()
    await db.refresh(reserva)
    return reserva_to_response(reserva)


async def cancelar_reserva_service(
    db: AsyncSession,
    reserva_id: uuid.UUID,
    current_user: User,
) -> ReservaResponse:
    stmt = select(Reserva).where(
        Reserva.id == reserva_id,
        Reserva.viajero_id == current_user.id,
    )
    result = await db.execute(stmt)
    reserva = result.scalar_one_or_none()

    if reserva is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reserva no encontrada",
        )

    if reserva.estado == EstadoReserva.cancelada.value:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="La reserva ya esta cancelada",
        )

    if reserva.estado not in [
        EstadoReserva.pendiente.value,
        EstadoReserva.confirmada.value,
    ]:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="La reserva no puede ser cancelada en su estado actual",
        )

    reserva.estado = EstadoReserva.cancelada.value
    await db.commit()
    await db.refresh(reserva)
    return reserva_to_response(reserva)
