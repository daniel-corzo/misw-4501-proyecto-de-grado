import uuid
from datetime import UTC, date, datetime, time, timezone

from fastapi import HTTPException, status
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from travelhub_common.security import User, RoleEnum

from app.models.reserva import Reserva
from app.schemas.reserva import (
    CrearReservaRequest,
    EstadoReserva,
    HabitacionReservaDetalleResponse,
    ModificarReservaRequest,
    ReservaDetalleResponse,
    ReservaHabitacionDetalleCompletoResponse,
    ReservaHotelDetalleResponse,
    ReservaResponse,
    ListaReservasResponse,
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


async def _habitacion_tiene_conflicto(
    db: AsyncSession,
    habitacion_id: uuid.UUID,
    check_in: datetime,
    check_out: datetime,
    exclude_reserva_id: uuid.UUID | None = None,
) -> bool:
    conditions = [
        Reserva.habitaciones_ids.contains([habitacion_id]),
        Reserva.check_in < check_out,
        Reserva.check_out > check_in,
        Reserva.estado.in_([EstadoReserva.pendiente.value, EstadoReserva.confirmada.value]),
    ]
    if exclude_reserva_id is not None:
        conditions.append(Reserva.id != exclude_reserva_id)
    stmt = select(Reserva.id).where(and_(*conditions)).limit(1)
    conflict = await db.execute(stmt)
    return conflict.scalar_one_or_none() is not None


async def crear_reserva_service(
    db: AsyncSession,
    body: CrearReservaRequest,
    current_user: User,
) -> ReservaResponse:
    check_in = _fecha_to_utc_start(body.fecha_entrada)
    check_out = _fecha_to_utc_start(body.fecha_salida)

    if await _habitacion_tiene_conflicto(db, body.habitacion_id, check_in, check_out):
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
            detail="La reserva ya está cancelada",
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


async def modificar_reserva_service(
    db: AsyncSession,
    reserva_id: uuid.UUID,
    body: ModificarReservaRequest,
    current_user: User,
) -> Reserva:
    stmt = select(Reserva).where(Reserva.id == reserva_id)
    result = await db.execute(stmt)
    reserva = result.scalar_one_or_none()
    if reserva is None or reserva.viajero_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reserva no encontrada",
        )

    if reserva.estado not in (
        EstadoReserva.pendiente.value,
        EstadoReserva.confirmada.value,
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se puede modificar una reserva en este estado",
        )

    now_utc = datetime.now(UTC)
    if reserva.check_out < now_utc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede modificar una reserva pasada",
        )

    fecha_entrada = (
        body.fecha_entrada
        if body.fecha_entrada is not None
        else reserva.check_in.date()
    )
    fecha_salida = (
        body.fecha_salida
        if body.fecha_salida is not None
        else reserva.check_out.date()
    )
    check_in = _fecha_to_utc_start(fecha_entrada)
    check_out = _fecha_to_utc_start(fecha_salida)

    if check_out <= check_in:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="fecha_salida debe ser posterior a fecha_entrada",
        )

    if body.habitacion_id is not None:
        habitacion_id = body.habitacion_id
    else:
        habitacion_id = (
            reserva.habitaciones_ids[0] if reserva.habitaciones_ids else None
        )
        if habitacion_id is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Reserva sin habitaciones asociadas",
            )

    if await _habitacion_tiene_conflicto(
        db,
        habitacion_id,
        check_in,
        check_out,
        exclude_reserva_id=reserva.id,
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="La habitación ya tiene una reserva activa en las fechas solicitadas",
        )

    reserva.check_in = check_in
    reserva.check_out = check_out
    reserva.habitaciones_ids = [habitacion_id]
    if body.num_huespedes is not None:
        reserva.personas = body.num_huespedes

    await db.flush()
    await db.commit()
    await db.refresh(reserva)
    return reserva


async def listar_reservas_usuario_service(
    db: AsyncSession,
    usuario_id: uuid.UUID,
    skip: int,
    limit: int,
    current_user: User,
) -> ListaReservasResponse:
    if current_user.role != RoleEnum.ADMIN and current_user.id != usuario_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para ver las reservas de este usuario",
        )

    # Count overall
    count_query = select(func.count(Reserva.id)).where(Reserva.viajero_id == usuario_id)
    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    # Get page
    stmt = (
        select(Reserva)
        .where(Reserva.viajero_id == usuario_id)
        .order_by(Reserva.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    reservas = result.scalars().all()

    return ListaReservasResponse(
        total=total,
        reservas=[reserva_to_response(r) for r in reservas]
    )
