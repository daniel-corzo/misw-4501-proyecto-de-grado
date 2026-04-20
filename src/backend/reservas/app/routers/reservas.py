import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, status, Depends, Request, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.reserva import Reserva
from app.schemas.reserva import (
    CrearReservaRequest,
    FiltroReservasUsuario,
    ReservaResponse,
    EstadoReserva,
    ListaReservasHotelResponse,
    ListaReservasResponse,
    ReservaDetalleResponse,
)
from app.services.hotel_service import obtener_habitaciones_hotel
from app.services.hotel_service import obtener_detalles_habitaciones_por_ids
from app.services.reserva_service import (
    cancelar_reserva_service,
    crear_reserva_service,
    reserva_to_detalle_response,
    reserva_to_response,
)
from travelhub_common.security import get_current_user, User

router = APIRouter(prefix="/reservas", tags=["reservas"])


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
async def listar_reservas_usuario(
    request: Request,
    estado: FiltroReservasUsuario,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    now_utc = datetime.now(UTC)
    stmt = select(Reserva).where(Reserva.viajero_id == current_user.id)

    if estado == FiltroReservasUsuario.canceladas:
        stmt = stmt.where(Reserva.estado == EstadoReserva.cancelada.value)
    elif estado == FiltroReservasUsuario.activas:
        stmt = stmt.where(
            Reserva.estado.in_([
                EstadoReserva.pendiente.value,
                EstadoReserva.confirmada.value,
            ]),
            Reserva.check_out >= now_utc,
        )
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
            )
        )

    return ListaReservasResponse(total=len(reservas), reservas=reservas)


@router.get("/hoteles", response_model=ListaReservasHotelResponse, status_code=status.HTTP_200_OK)
async def listar_reservas_hotel(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    habitaciones = await obtener_habitaciones_hotel(request.headers.get("Authorization"))
    habitacion_ids = [habitacion.id for habitacion in habitaciones]

    if not habitacion_ids:
        return ListaReservasHotelResponse(total=0, reservas=[], habitaciones=[])

    stmt = select(Reserva).where(Reserva.habitaciones_ids.overlap(habitacion_ids))

    stmt = stmt.order_by(Reserva.created_at.desc())
    result = await db.execute(stmt)
    reservas = [reserva_to_response(r) for r in result.scalars().all()]
    return ListaReservasHotelResponse(
        total=len(reservas),
        reservas=reservas,
        habitaciones=habitaciones,
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
            detail="No fue posible obtener el detalle de la habitacion asociada",
        )

    return reserva_to_detalle_response(reserva, detalle_habitacion)


@router.patch("/{reserva_id}/cancelar", response_model=ReservaResponse, status_code=status.HTTP_200_OK)
async def cancelar_reserva(
    reserva_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await cancelar_reserva_service(
        db=db,
        reserva_id=reserva_id,
        current_user=current_user,
    )
