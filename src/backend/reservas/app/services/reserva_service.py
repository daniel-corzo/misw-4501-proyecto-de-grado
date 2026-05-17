import json
import uuid
from datetime import UTC, date, datetime, time, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from travelhub_common.security import User, RoleEnum

from app.models.reserva import Reserva
from app.schemas.reserva import (
    CrearReservaRequest,
    EstadoPagoDetalle,
    EstadoReserva,
    EstadoPagoFiltro,
    EstadoPagoReserva,
    HabitacionHotelResponse,
    HabitacionReservaDetalleResponse,
    IngresoMensualResponse,
    ListaReservasHotelResponse,
    MiHotelResponse,
    ModificarReservaRequest,
    OcupacionHabitacionResponse,
    OcupacionMensualResponse,
    PagoReservaDetalleResponse,
    ReporteIngresosResponse,
    ReporteOcupacionResponse,
    ReservaDetalleResponse,
    ReservaHabitacionDetalleCompletoResponse,
    ReservaHotelDetalleCompletoResponse,
    ReservaHotelResponse,
    ReservaHotelDetalleResponse,
    ReservaResponse,
    ListaReservasResponse,
    ViajeroReservaDetalleResponse,
)
from app.services.hotel_service import (
    obtener_detalles_habitaciones_por_ids,
    obtener_habitaciones_hotel,
    obtener_mi_hotel,
)
from app.services.pago_service import obtener_pagos_por_ids
from app.services.usuario_service import obtener_usuarios_resumen_por_ids


def _fecha_to_utc_start(d: date) -> datetime:
    return datetime.combine(d, time.min, tzinfo=timezone.utc)


def _codigo_reserva(reserva: Reserva) -> str:
    return f"TH-{str(reserva.id).split('-')[0].upper()}"


def _calcular_total_noches(reserva: Reserva) -> int:
    return max((reserva.check_out.date() - reserva.check_in.date()).days, 0)


def _calcular_monto_total(
    reserva: Reserva,
    detalle_habitacion: HabitacionReservaDetalleResponse | None,
) -> int | None:
    if detalle_habitacion is None or detalle_habitacion.monto_habitacion is None:
        return None

    return _calcular_total_noches(reserva) * (
        detalle_habitacion.monto_habitacion
        + (detalle_habitacion.impuestos_habitacion or 0)
    )


def _build_qr_checkin_payload(
    reserva: Reserva,
    detalle_habitacion: HabitacionReservaDetalleResponse,
) -> str:
    habitacion_id = reserva.habitaciones_ids[0] if reserva.habitaciones_ids else None
    if habitacion_id is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Reserva sin habitaciones asociadas",
        )

    payload = {
        "codigo_reserva": _codigo_reserva(reserva),
        "fecha_entrada": reserva.check_in.date().isoformat(),
        "fecha_salida": reserva.check_out.date().isoformat(),
        "habitacion_id": str(habitacion_id),
        "habitacion_nombre": detalle_habitacion.nombre_habitacion,
        "hotel_id": str(detalle_habitacion.hotel_id)
        if detalle_habitacion.hotel_id
        else None,
        "hotel_nombre": detalle_habitacion.nombre_hotel,
        "numero_habitacion": detalle_habitacion.numero_habitacion,
        "reserva_id": str(reserva.id),
    }
    return json.dumps(
        payload,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    )


def _build_pago_detalle_response(pago) -> PagoReservaDetalleResponse:
    if pago is None:
        return PagoReservaDetalleResponse(estado=EstadoPagoDetalle.pending)

    return PagoReservaDetalleResponse(
        id=pago.id,
        estado=EstadoPagoDetalle(pago.estado),
        monto=getattr(pago, "monto", None),
        medio_de_pago=getattr(pago, "medio_de_pago", None),
        created_at=getattr(pago, "created_at", None),
        tarjeta_ultimos_4=getattr(pago, "tarjeta_ultimos_4", None),
    )


def reserva_to_response(
    reserva: Reserva,
    nombre_habitacion: str | None = None,
    nombre_hotel: str | None = None,
    imagenes_hotel: list[str] | None = None,
    ciudad_hotel: str | None = None,
    pais_hotel: str | None = None,
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
        ciudad_hotel=ciudad_hotel,
        pais_hotel=pais_hotel,
        fecha_entrada=reserva.check_in.date(),
        fecha_salida=reserva.check_out.date(),
        num_huespedes=reserva.personas,
        estado=EstadoReserva(reserva.estado),
        pago_id=reserva.pago_id,
        created_at=reserva.created_at,
    )


def reserva_to_hotel_response(
    reserva: Reserva,
    nombre_habitacion: str | None = None,
    nombre_hotel: str | None = None,
    imagenes_hotel: list[str] | None = None,
    ciudad_hotel: str | None = None,
    pais_hotel: str | None = None,
    nombre_viajero: str | None = None,
    email_viajero: str | None = None,
    numero_habitacion: str | None = None,
    monto_total: int | None = None,
    estado_pago: str | None = None,
) -> ReservaHotelResponse:
    base_response = reserva_to_response(
        reserva,
        nombre_habitacion=nombre_habitacion,
        nombre_hotel=nombre_hotel,
        imagenes_hotel=imagenes_hotel,
        ciudad_hotel=ciudad_hotel,
        pais_hotel=pais_hotel,
    )
    return ReservaHotelResponse(
        **base_response.model_dump(),
        nombre_viajero=nombre_viajero,
        email_viajero=email_viajero,
        numero_habitacion=numero_habitacion,
        total_noches=_calcular_total_noches(reserva),
        monto_total=monto_total,
        estado_pago=EstadoPagoReserva(estado_pago) if estado_pago else None,
    )


def reserva_to_hotel_detalle_response(
    reserva: Reserva,
    detalle_habitacion: HabitacionReservaDetalleResponse,
    viajero,
    pago,
) -> ReservaHotelDetalleCompletoResponse:
    base_response = reserva_to_detalle_response(reserva, detalle_habitacion)

    return ReservaHotelDetalleCompletoResponse(
        **base_response.model_dump(),
        viajero=ViajeroReservaDetalleResponse(
            id=reserva.viajero_id,
            nombre=getattr(viajero, "nombre", None),
            email=getattr(viajero, "email", None),
        ),
        pago=_build_pago_detalle_response(pago),
        total_noches=_calcular_total_noches(reserva),
        monto_total=_calcular_monto_total(reserva, detalle_habitacion),
        qr_checkin_payload=_build_qr_checkin_payload(reserva, detalle_habitacion),
    )


async def construir_reservas_hotel_response(
    authorization_header: str | None,
    reservas_db: list[Reserva],
) -> list[ReservaHotelResponse]:
    if not reservas_db:
        return []

    habitacion_ids = list(
        {
            habitacion_id
            for reserva in reservas_db
            for habitacion_id in (reserva.habitaciones_ids or [])
        }
    )
    detalles_por_habitacion = await obtener_detalles_habitaciones_por_ids(
        authorization_header,
        habitacion_ids,
    )

    viajero_ids = list({reserva.viajero_id for reserva in reservas_db})
    viajeros_por_id = await obtener_usuarios_resumen_por_ids(
        authorization_header,
        viajero_ids,
    )

    pago_ids = list(
        {reserva.pago_id for reserva in reservas_db if reserva.pago_id is not None}
    )
    pagos_por_id = await obtener_pagos_por_ids(authorization_header, pago_ids)

    reservas: list[ReservaHotelResponse] = []
    for reserva in reservas_db:
        habitacion_id = reserva.habitaciones_ids[0] if reserva.habitaciones_ids else None
        detalle_habitacion = (
            detalles_por_habitacion.get(habitacion_id) if habitacion_id else None
        )
        viajero = viajeros_por_id.get(reserva.viajero_id)
        pago = pagos_por_id.get(reserva.pago_id) if reserva.pago_id else None

        reservas.append(
            reserva_to_hotel_response(
                reserva,
                nombre_habitacion=(
                    detalle_habitacion.nombre_habitacion if detalle_habitacion else None
                ),
                nombre_hotel=(
                    detalle_habitacion.nombre_hotel if detalle_habitacion else None
                ),
                imagenes_hotel=(
                    detalle_habitacion.imagenes_hotel if detalle_habitacion else []
                ),
                ciudad_hotel=(
                    detalle_habitacion.ciudad_hotel if detalle_habitacion else None
                ),
                pais_hotel=(
                    detalle_habitacion.pais_hotel if detalle_habitacion else None
                ),
                nombre_viajero=viajero.nombre if viajero else None,
                email_viajero=viajero.email if viajero else None,
                numero_habitacion=(
                    detalle_habitacion.numero_habitacion if detalle_habitacion else None
                ),
                monto_total=_calcular_monto_total(reserva, detalle_habitacion),
                estado_pago=pago.estado if pago else None,
            )
        )

    return reservas


async def listar_reservas_hotel_service(
    db: AsyncSession,
    authorization_header: str | None,
    skip: int,
    limit: int,
    nombre_viajero: str | None = None,
    tipo_habitacion: str | None = None,
    estado: EstadoReserva | None = None,
    fecha_inicio: date | None = None,
    fecha_fin: date | None = None,
    estado_pago: EstadoPagoFiltro | None = None,
    num_huespedes: int | None = None,
) -> ListaReservasHotelResponse:
    habitaciones = await obtener_habitaciones_hotel(authorization_header)
    habitacion_ids = [habitacion.id for habitacion in habitaciones]

    if not habitacion_ids:
        return ListaReservasHotelResponse(total=0, reservas=[], habitaciones=[])

    # Build SQL-level conditions (fields available in DB)
    conditions: list = [Reserva.habitaciones_ids.overlap(habitacion_ids)]
    if estado is not None:
        conditions.append(Reserva.estado == estado.value)
    if num_huespedes is not None:
        conditions.append(Reserva.personas == num_huespedes)
    if fecha_inicio is not None:
        # Overlap: reservation check_out must be after start of fecha_inicio
        conditions.append(Reserva.check_out > _fecha_to_utc_start(fecha_inicio))
    if fecha_fin is not None:
        # Overlap: reservation check_in must be before end of fecha_fin
        conditions.append(
            Reserva.check_in < _fecha_to_utc_start(fecha_fin) + timedelta(days=1)
        )

    has_memory_filters = bool(nombre_viajero or tipo_habitacion or estado_pago is not None)

    if has_memory_filters:
        # Fetch all SQL-matching candidates, enrich, then filter in memory
        stmt = (
            select(Reserva)
            .where(and_(*conditions))
            .order_by(Reserva.check_in.asc(), Reserva.created_at.desc())
        )
        result = await db.execute(stmt)
        reservas_db = list(result.scalars().all())

        all_responses = await construir_reservas_hotel_response(
            authorization_header,
            reservas_db,
        )

        # Apply in-memory filters
        if nombre_viajero:
            q = nombre_viajero.strip().lower()
            all_responses = [
                r for r in all_responses
                if (r.nombre_viajero and q in r.nombre_viajero.lower())
                or (r.email_viajero and q in r.email_viajero.lower())
            ]
        if tipo_habitacion:
            q = tipo_habitacion.strip().lower()
            all_responses = [
                r for r in all_responses
                if r.nombre_habitacion and q in r.nombre_habitacion.lower()
            ]
        if estado_pago is not None:
            if estado_pago == EstadoPagoFiltro.pending:
                all_responses = [r for r in all_responses if r.estado_pago is None]
            else:
                all_responses = [
                    r for r in all_responses
                    if r.estado_pago is not None and r.estado_pago.value == estado_pago.value
                ]

        total = len(all_responses)
        reservas = all_responses[skip: skip + limit]
    else:
        # Efficient path: SQL count + paginated query (no in-memory filters)
        total_result = await db.execute(
            select(func.count(Reserva.id)).where(and_(*conditions))
        )
        total = total_result.scalar_one()

        stmt = (
            select(Reserva)
            .where(and_(*conditions))
            .order_by(Reserva.check_in.asc(), Reserva.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(stmt)
        reservas_db = result.scalars().all()
        reservas = await construir_reservas_hotel_response(
            authorization_header,
            reservas_db,
        )

    # Enrich habitaciones list with nombre_habitacion for the frontend dropdown
    detalles_hab = await obtener_detalles_habitaciones_por_ids(
        authorization_header, habitacion_ids
    )
    habitaciones_enriquecidas = [
        hab.model_copy(
            update={
                "nombre_habitacion": (
                    detalles_hab[hab.id].nombre_habitacion
                    if hab.id in detalles_hab
                    else None
                )
            }
        )
        for hab in habitaciones
    ]

    return ListaReservasHotelResponse(
        total=total,
        reservas=reservas,
        habitaciones=habitaciones_enriquecidas,
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
        codigo_reserva=_codigo_reserva(reserva),
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


async def obtener_reserva_hotel_detalle_service(
    db: AsyncSession,
    authorization_header: str | None,
    reserva_id: uuid.UUID,
    habitacion_ids_hotel: list[uuid.UUID],
) -> ReservaHotelDetalleCompletoResponse:
    result = await db.execute(select(Reserva).where(Reserva.id == reserva_id))
    reserva = result.scalar_one_or_none()

    if reserva is None or not set(reserva.habitaciones_ids or []).intersection(
        habitacion_ids_hotel
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reserva no encontrada",
        )

    habitacion_id = reserva.habitaciones_ids[0] if reserva.habitaciones_ids else None
    if habitacion_id is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Reserva sin habitaciones asociadas",
        )

    detalles_por_habitacion = await obtener_detalles_habitaciones_por_ids(
        authorization_header,
        [habitacion_id],
    )
    detalle_habitacion = detalles_por_habitacion.get(habitacion_id)
    if detalle_habitacion is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No fue posible obtener el detalle de la habitación asociada",
        )

    viajeros_por_id = await obtener_usuarios_resumen_por_ids(
        authorization_header,
        [reserva.viajero_id],
    )
    pagos_por_id = await obtener_pagos_por_ids(
        authorization_header,
        [reserva.pago_id] if reserva.pago_id is not None else [],
    )

    viajero = viajeros_por_id.get(reserva.viajero_id)
    pago = pagos_por_id.get(reserva.pago_id) if reserva.pago_id else None
    return reserva_to_hotel_detalle_response(
        reserva,
        detalle_habitacion,
        viajero,
        pago,
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


async def confirmar_reserva_service(
    db: AsyncSession,
    reserva_id: uuid.UUID,
    habitacion_ids_hotel: list[uuid.UUID],
) -> Reserva:
    result = await db.execute(select(Reserva).where(Reserva.id == reserva_id))
    reserva = result.scalar_one_or_none()

    if reserva is None or not set(reserva.habitaciones_ids or []).intersection(
        habitacion_ids_hotel
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reserva no encontrada",
        )

    if reserva.estado != EstadoReserva.pendiente.value:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="La reserva no puede ser confirmada en su estado actual",
        )

    reserva.estado = EstadoReserva.confirmada.value
    await db.flush()
    await db.commit()
    await db.refresh(reserva)
    return reserva


async def rechazar_reserva_service(
    db: AsyncSession,
    reserva_id: uuid.UUID,
    habitacion_ids_hotel: list[uuid.UUID],
) -> Reserva:
    result = await db.execute(select(Reserva).where(Reserva.id == reserva_id))
    reserva = result.scalar_one_or_none()

    if reserva is None or not set(reserva.habitaciones_ids or []).intersection(
        habitacion_ids_hotel
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reserva no encontrada",
        )

    if reserva.estado == EstadoReserva.cancelada.value:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="La reserva ya está cancelada",
        )

    if reserva.estado not in (
        EstadoReserva.pendiente.value,
        EstadoReserva.confirmada.value,
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="La reserva no puede ser rechazada en su estado actual",
        )

    reserva.estado = EstadoReserva.cancelada.value
    await db.flush()
    await db.commit()
    await db.refresh(reserva)
    return reserva


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
    if body.pago_id is not None:
        if reserva.estado != EstadoReserva.pendiente.value:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Solo se puede asociar un pago a una reserva pendiente",
            )
        if reserva.pago_id is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="La reserva ya tiene un pago asociado",
            )
        reserva.pago_id = body.pago_id

    await db.flush()
    await db.commit()
    await db.refresh(reserva)
    return reserva


async def eliminar_reserva_service(
    db: AsyncSession,
    reserva_id: uuid.UUID,
    current_user: User,
) -> None:
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

    if reserva.estado not in (
        EstadoReserva.pendiente.value,
        EstadoReserva.cancelada.value,
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Solo se pueden eliminar reservas pendientes o canceladas",
        )

    await db.delete(reserva)
    await db.commit()


async def generar_reporte_ingresos_service(
    db: AsyncSession,
    authorization_header: str | None,
) -> ReporteIngresosResponse:
    habitaciones = await obtener_habitaciones_hotel(authorization_header)
    habitacion_ids = [habitacion.id for habitacion in habitaciones]

    if not habitacion_ids:
        return ReporteIngresosResponse(
            nombre_hotel=None,
            ingresos_por_mes=[],
            total_general=0,
            total_pagos=0,
        )

    stmt = (
        select(Reserva)
        .where(
            and_(
                Reserva.habitaciones_ids.overlap(habitacion_ids),
                Reserva.pago_id.isnot(None),
            )
        )
    )
    result = await db.execute(stmt)
    reservas_db = list(result.scalars().all())

    pago_ids = list({reserva.pago_id for reserva in reservas_db if reserva.pago_id is not None})
    pagos_por_id = await obtener_pagos_por_ids(authorization_header, pago_ids)

    nombre_hotel: str | None = None
    if habitacion_ids:
        detalles = await obtener_detalles_habitaciones_por_ids(authorization_header, [habitacion_ids[0]])
        detalle = detalles.get(habitacion_ids[0])
        if detalle:
            nombre_hotel = detalle.nombre_hotel

    ingresos_por_mes: dict[tuple[int, int], dict] = {}
    for reserva in reservas_db:
        if reserva.pago_id is None:
            continue
        pago = pagos_por_id.get(reserva.pago_id)
        if pago is None or pago.estado != "successful":
            continue
        if pago.created_at is None or pago.monto is None:
            continue
        key = (pago.created_at.year, pago.created_at.month)
        if key not in ingresos_por_mes:
            ingresos_por_mes[key] = {"total_pagos": 0, "ingresos_totales": 0}
        ingresos_por_mes[key]["total_pagos"] += 1
        ingresos_por_mes[key]["ingresos_totales"] += pago.monto

    ingresos_lista = [
        IngresoMensualResponse(
            anio=anio,
            mes=mes,
            total_pagos=datos["total_pagos"],
            ingresos_totales=datos["ingresos_totales"],
        )
        for (anio, mes), datos in sorted(ingresos_por_mes.items())
    ]

    total_general = sum(i.ingresos_totales for i in ingresos_lista)
    total_pagos = sum(i.total_pagos for i in ingresos_lista)

    return ReporteIngresosResponse(
        nombre_hotel=nombre_hotel,
        ingresos_por_mes=ingresos_lista,
        total_general=total_general,
        total_pagos=total_pagos,
    )


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


async def generar_reporte_ocupacion_service(
    db: AsyncSession,
    authorization_header: str | None,
) -> ReporteOcupacionResponse:
    habitaciones = await obtener_habitaciones_hotel(authorization_header)
    habitacion_ids = [h.id for h in habitaciones]

    empty = ReporteOcupacionResponse(
        nombre_hotel=None,
        fecha_registro=None,
        total_habitaciones=0,
        ocupacion_por_mes=[],
        ocupacion_por_habitacion=[],
        noches_ocupadas_totales=0,
        noches_disponibles_totales=0,
        tasa_ocupacion_global=0.0,
    )

    if not habitacion_ids:
        return empty

    mi_hotel: MiHotelResponse = await obtener_mi_hotel(authorization_header)
    habitacion_ids_set = set(habitacion_ids)

    # Query confirmed/completed reservations that overlap with any hotel room
    stmt = select(Reserva).where(
        and_(
            Reserva.habitaciones_ids.overlap(habitacion_ids),
            Reserva.estado.in_(["confirmada", "completada"]),
        )
    )
    result = await db.execute(stmt)
    reservas_db = list(result.scalars().all())

    # Build month-based calendar from hotel registration to today
    start_date = mi_hotel.created_at.date() if mi_hotel.created_at else date.today()
    end_date = date.today()

    if start_date > end_date:
        start_date = end_date

    total_days = (end_date - start_date).days + 1
    total_habitaciones = len(habitaciones)

    # Build per-month day ranges within [start_date, end_date]
    months: list[tuple[int, int]] = []
    cur = date(start_date.year, start_date.month, 1)
    while cur <= end_date:
        months.append((cur.year, cur.month))
        if cur.month == 12:
            cur = date(cur.year + 1, 1, 1)
        else:
            cur = date(cur.year, cur.month + 1, 1)

    import calendar as _cal
    noches_por_mes: dict[tuple[int, int], int] = {m: 0 for m in months}
    noches_por_hab: dict[uuid.UUID, int] = {hid: 0 for hid in habitacion_ids}

    for reserva in reservas_db:
        ci = reserva.check_in.date() if hasattr(reserva.check_in, 'date') else reserva.check_in
        co = reserva.check_out.date() if hasattr(reserva.check_out, 'date') else reserva.check_out

        # Only rooms that belong to this hotel
        hab_ids_in_reserva = [
            uid for uid in (reserva.habitaciones_ids or [])
            if uid in habitacion_ids_set
        ]
        if not hab_ids_in_reserva:
            continue

        # Iterate each night in [check_in, check_out)
        night = ci
        while night < co:
            if start_date <= night <= end_date:
                key = (night.year, night.month)
                if key in noches_por_mes:
                    noches_por_mes[key] += len(hab_ids_in_reserva)
                for hid in hab_ids_in_reserva:
                    if hid in noches_por_hab:
                        noches_por_hab[hid] += 1
            night += timedelta(days=1)

    # Build monthly response with denominators
    hab_info = {h.id: h for h in habitaciones}
    ocupacion_por_mes: list[OcupacionMensualResponse] = []
    for (anio, mes) in sorted(months):
        days_in_month = _cal.monthrange(anio, mes)[1]
        month_start = date(anio, mes, 1)
        month_end = date(anio, mes, days_in_month)
        effective_start = max(month_start, start_date)
        effective_end = min(month_end, end_date)
        dias_efectivos = (effective_end - effective_start).days + 1
        noches_disp = total_habitaciones * dias_efectivos
        noches_ocup = noches_por_mes.get((anio, mes), 0)
        tasa = round(noches_ocup / noches_disp * 100, 2) if noches_disp > 0 else 0.0
        ocupacion_por_mes.append(
            OcupacionMensualResponse(
                anio=anio,
                mes=mes,
                noches_ocupadas=noches_ocup,
                noches_disponibles=noches_disp,
                tasa_ocupacion=tasa,
            )
        )

    # Build per-room response
    ocupacion_por_habitacion: list[OcupacionHabitacionResponse] = []
    noches_disp_total = total_habitaciones * total_days
    for hid in habitacion_ids:
        h = hab_info[hid]
        noches_ocup = noches_por_hab.get(hid, 0)
        tasa = round(noches_ocup / total_days * 100, 2) if total_days > 0 else 0.0
        ocupacion_por_habitacion.append(
            OcupacionHabitacionResponse(
                habitacion_id=hid,
                numero=h.numero,
                capacidad=h.capacidad,
                noches_ocupadas=noches_ocup,
                noches_disponibles=total_days,
                tasa_ocupacion=tasa,
            )
        )
    ocupacion_por_habitacion.sort(key=lambda x: x.numero)

    noches_ocupadas_totales = sum(o.noches_ocupadas for o in ocupacion_por_mes)
    tasa_global = (
        round(noches_ocupadas_totales / noches_disp_total * 100, 2)
        if noches_disp_total > 0
        else 0.0
    )

    return ReporteOcupacionResponse(
        nombre_hotel=mi_hotel.nombre,
        fecha_registro=mi_hotel.created_at,
        total_habitaciones=total_habitaciones,
        ocupacion_por_mes=ocupacion_por_mes,
        ocupacion_por_habitacion=ocupacion_por_habitacion,
        noches_ocupadas_totales=noches_ocupadas_totales,
        noches_disponibles_totales=noches_disp_total,
        tasa_ocupacion_global=tasa_global,
    )
