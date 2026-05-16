import uuid
import logging
from datetime import UTC, date, datetime
from typing import Optional

from fastapi import APIRouter, status, Depends, Request, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.reserva import Reserva
from app.schemas.reserva import (
    CrearReservaRequest,
    EstadoReserva,
    EstadoPagoFiltro,
    FiltroReservasUsuario,
    ModificarReservaRequest,
    ReporteIngresosResponse,
    ReservaResponse,
    ListaReservasHotelResponse,
    ListaReservasResponse,
    ReservaDetalleResponse,
    ReservaHotelDetalleCompletoResponse,
    ReservaHotelResponse,
)
from app.services.hotel_service import obtener_habitaciones_hotel
from app.services.hotel_service import obtener_detalles_habitaciones_por_ids
from app.services.reserva_service import (
    cancelar_reserva_service,
    construir_reservas_hotel_response,
    confirmar_reserva_service,
    crear_reserva_service,
    enviar_correo_estado_reserva,
    eliminar_reserva_service,
    generar_reporte_ingresos_service,
    listar_reservas_hotel_service,
    rechazar_reserva_service,
    reserva_to_detalle_response,
    reserva_to_response,
    modificar_reserva_service,
    listar_reservas_usuario_service,
    obtener_reserva_hotel_detalle_service,
)
from travelhub_common.booking_email import BookingEmailEvent
from travelhub_common.security import RoleChecker, RoleEnum, User, get_current_user

router = APIRouter(prefix="/reservas", tags=["reservas"])
logger = logging.getLogger(__name__)


@router.post("", response_model=ReservaResponse, status_code=status.HTTP_201_CREATED)
async def crear_reserva(
    body: CrearReservaRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Crea una nueva reserva de habitacion.

    En la implementacion futura:
    - Verificar disponibilidad via habitaciones del servicio de hoteles
    - Publicar evento 'reserva_creada' en SQS para notificaciones
    """
    return await crear_reserva_service(db=db, body=body, current_user=current_user)


@router.get("", response_model=ListaReservasResponse, status_code=status.HTTP_200_OK)
async def listar_reservas_por_estado(
    request: Request,
    estado: FiltroReservasUsuario,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    now_utc = datetime.now(UTC)
    stmt = select(Reserva).where(Reserva.viajero_id == current_user.id)

    if estado == FiltroReservasUsuario.canceladas:
        stmt = stmt.where(Reserva.estado == EstadoReserva.cancelada.value)
        stmt = stmt.order_by(Reserva.created_at.desc())
    elif estado == FiltroReservasUsuario.activas:
        stmt = stmt.where(
            Reserva.estado.in_([
                EstadoReserva.pendiente.value,
                EstadoReserva.confirmada.value,
            ]),
            Reserva.check_out >= now_utc,
        )
        stmt = stmt.order_by(Reserva.check_in.asc())
    elif estado == FiltroReservasUsuario.pasadas:
        stmt = stmt.where(
            Reserva.estado != EstadoReserva.cancelada.value,
            Reserva.check_out < now_utc,
        )
        stmt = stmt.order_by(Reserva.created_at.desc())
    result = await db.execute(stmt)
    reservas_db = result.scalars().all()

    habitacion_ids = list(
        {
            habitacion_id
            for reserva in reservas_db
            for habitacion_id in (reserva.habitaciones_ids or [])
        }
    )
    detalles_por_habitacion = await obtener_detalles_habitaciones_por_ids(
        request.headers.get("Authorization"),
        habitacion_ids,
    )

    reservas = []
    for reserva in reservas_db:
        habitacion_id = reserva.habitaciones_ids[0] if reserva.habitaciones_ids else None
        detalle_habitacion = detalles_por_habitacion.get(habitacion_id) if habitacion_id else None
        reservas.append(
            reserva_to_response(
                reserva,
                nombre_habitacion=detalle_habitacion.nombre_habitacion if detalle_habitacion else None,
                nombre_hotel=detalle_habitacion.nombre_hotel if detalle_habitacion else None,
                imagenes_hotel=detalle_habitacion.imagenes_hotel if detalle_habitacion else [],
                ciudad_hotel=detalle_habitacion.ciudad_hotel if detalle_habitacion else None,
                pais_hotel=detalle_habitacion.pais_hotel if detalle_habitacion else None,
            )
        )

    return ListaReservasResponse(total=len(reservas), reservas=reservas)


@router.get("/hoteles", response_model=ListaReservasHotelResponse, status_code=status.HTTP_200_OK)
async def listar_reservas_hotel(
    request: Request,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    nombre_viajero: Optional[str] = Query(None),
    tipo_habitacion: Optional[str] = Query(None),
    estado: Optional[EstadoReserva] = Query(None),
    fecha_inicio: Optional[date] = Query(None),
    fecha_fin: Optional[date] = Query(None),
    estado_pago: Optional[EstadoPagoFiltro] = Query(None),
    num_huespedes: Optional[int] = Query(None, ge=1),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await listar_reservas_hotel_service(
        db=db,
        authorization_header=request.headers.get("Authorization"),
        skip=skip,
        limit=limit,
        nombre_viajero=nombre_viajero,
        tipo_habitacion=tipo_habitacion,
        estado=estado,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        estado_pago=estado_pago,
        num_huespedes=num_huespedes,
    )


@router.get(
    "/hoteles/reporte-ingresos",
    response_model=ReporteIngresosResponse,
    status_code=status.HTTP_200_OK,
)
async def generar_reporte_ingresos(
    request: Request,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(RoleChecker([RoleEnum.MANAGER, RoleEnum.USER])),
):
    return await generar_reporte_ingresos_service(
        db=db,
        authorization_header=request.headers.get("Authorization"),
    )


@router.get(
    "/hoteles/{reserva_id}",
    response_model=ReservaHotelDetalleCompletoResponse,
    status_code=status.HTTP_200_OK,
)
async def obtener_reserva_hotel(
    reserva_id: uuid.UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(RoleChecker([RoleEnum.MANAGER, RoleEnum.USER])),
):
    authorization_header = request.headers.get("Authorization")
    habitaciones = await obtener_habitaciones_hotel(authorization_header)
    return await obtener_reserva_hotel_detalle_service(
        db=db,
        authorization_header=authorization_header,
        reserva_id=reserva_id,
        habitacion_ids_hotel=[habitacion.id for habitacion in habitaciones],
    )


@router.get("/{reserva_id}", response_model=ReservaDetalleResponse, status_code=status.HTTP_200_OK)
async def obtener_reserva(
    reserva_id: uuid.UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
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

    habitacion_id = reserva.habitaciones_ids[0] if reserva.habitaciones_ids else None
    if habitacion_id is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Reserva sin habitaciones asociadas",
        )

    detalles_por_habitacion = await obtener_detalles_habitaciones_por_ids(
        request.headers.get("Authorization"),
        [habitacion_id],
    )
    detalle_habitacion = detalles_por_habitacion.get(habitacion_id)
    if detalle_habitacion is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No fue posible obtener el detalle de la habitación asociada",
        )

    return reserva_to_detalle_response(reserva, detalle_habitacion)


@router.patch("/{reserva_id}", response_model=ReservaResponse, status_code=status.HTTP_200_OK)
async def modificar_reserva(
    request: Request,
    reserva_id: uuid.UUID,
    body: ModificarReservaRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Actualiza fechas, número de huéspedes y/o habitación de una reserva activa del viajero."""
    reserva = await modificar_reserva_service(
        db=db,
        reserva_id=reserva_id,
        body=body,
        current_user=current_user,
    )
    habitacion_id = reserva.habitaciones_ids[0] if reserva.habitaciones_ids else None
    if habitacion_id is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Reserva sin habitaciones asociadas",
        )
    detalles_por_habitacion = await obtener_detalles_habitaciones_por_ids(
        request.headers.get("Authorization"),
        [habitacion_id],
    )
    detalle = detalles_por_habitacion.get(habitacion_id)
    return reserva_to_response(
        reserva,
        nombre_habitacion=detalle.nombre_habitacion if detalle else None,
        nombre_hotel=detalle.nombre_hotel if detalle else None,
        imagenes_hotel=detalle.imagenes_hotel if detalle else [],
        ciudad_hotel=detalle.ciudad_hotel if detalle else None,
        pais_hotel=detalle.pais_hotel if detalle else None,
    )


@router.patch("/{reserva_id}/confirmar", response_model=ReservaHotelResponse, status_code=status.HTTP_200_OK)
async def confirmar_reserva(
    reserva_id: uuid.UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(RoleChecker([RoleEnum.MANAGER, RoleEnum.USER])),
):
    authorization_header = request.headers.get("Authorization")
    habitaciones = await obtener_habitaciones_hotel(authorization_header)
    reserva = await confirmar_reserva_service(
        db=db,
        reserva_id=reserva_id,
        habitacion_ids_hotel=[habitacion.id for habitacion in habitaciones],
    )
    reservas = await construir_reservas_hotel_response(authorization_header, [reserva])
    reserva_response = reservas[0]
    enviar_correo_estado_reserva(
        event=BookingEmailEvent.confirmed,
        reserva=reserva,
        recipient_email=reserva_response.email_viajero,
        hotel_name=reserva_response.nombre_hotel,
        room_name=reserva_response.nombre_habitacion,
        room_number=reserva_response.numero_habitacion,
        traveler_name=reserva_response.nombre_viajero,
        total_nights=reserva_response.total_noches,
        total_amount=reserva_response.monto_total,
    )
    return reserva_response


@router.patch("/{reserva_id}/rechazar", response_model=ReservaHotelResponse, status_code=status.HTTP_200_OK)
async def rechazar_reserva(
    reserva_id: uuid.UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(RoleChecker([RoleEnum.MANAGER, RoleEnum.USER])),
):
    authorization_header = request.headers.get("Authorization")
    habitaciones = await obtener_habitaciones_hotel(authorization_header)
    reserva = await rechazar_reserva_service(
        db=db,
        reserva_id=reserva_id,
        habitacion_ids_hotel=[habitacion.id for habitacion in habitaciones],
    )
    reservas = await construir_reservas_hotel_response(authorization_header, [reserva])
    reserva_response = reservas[0]
    enviar_correo_estado_reserva(
        event=BookingEmailEvent.cancelled,
        reserva=reserva,
        recipient_email=reserva_response.email_viajero,
        hotel_name=reserva_response.nombre_hotel,
        room_name=reserva_response.nombre_habitacion,
        room_number=reserva_response.numero_habitacion,
        traveler_name=reserva_response.nombre_viajero,
        total_nights=reserva_response.total_noches,
        total_amount=reserva_response.monto_total,
    )
    return reserva_response


@router.delete("/{reserva_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_reserva(
    reserva_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Elimina permanentemente una reserva pendiente o cancelada del viajero."""
    await eliminar_reserva_service(db=db, reserva_id=reserva_id, current_user=current_user)


@router.patch("/{reserva_id}/cancelar", response_model=ReservaResponse, status_code=status.HTTP_200_OK)
async def cancelar_reserva(
    reserva_id: uuid.UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    reserva = await cancelar_reserva_service(
        db=db,
        reserva_id=reserva_id,
        current_user=current_user,
    )
    habitacion_id = reserva.habitacion_id
    if habitacion_id is not None:
        try:
            detalles_por_habitacion = await obtener_detalles_habitaciones_por_ids(
                request.headers.get("Authorization"),
                [habitacion_id],
            )
            detalle = detalles_por_habitacion.get(habitacion_id)
            if detalle is not None:
                enviar_correo_estado_reserva(
                    event=BookingEmailEvent.cancelled,
                    reserva=reserva,
                    recipient_email=current_user.email,
                    hotel_name=detalle.nombre_hotel,
                    room_name=detalle.nombre_habitacion,
                    room_number=detalle.numero_habitacion,
                )
        except HTTPException as exc:
            if exc.status_code in (
                status.HTTP_502_BAD_GATEWAY,
                status.HTTP_503_SERVICE_UNAVAILABLE,
            ):
                logger.exception(
                    "No fue posible preparar el correo de cancelación para la reserva %s (status=%s, detail=%s)",
                    reserva.id,
                    exc.status_code,
                    exc.detail,
                )
            else:
                raise
    return reserva


@router.get("/usuario/{usuario_id}", response_model=ListaReservasResponse, status_code=status.HTTP_200_OK)
async def listar_reservas_usuario(
    usuario_id: uuid.UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await listar_reservas_usuario_service(db=db, usuario_id=usuario_id, skip=skip, limit=limit, current_user=current_user)
