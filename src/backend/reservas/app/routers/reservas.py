import uuid
from datetime import UTC, datetime, date

from fastapi import APIRouter, status, Depends, Request
from sqlalchemy import or_, select
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
)
from app.services.hotel_service import obtener_habitaciones_hotel
from app.services.hotel_service import obtener_detalles_habitaciones_por_ids
from app.services.reserva_service import crear_reserva_service, reserva_to_response
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

    habitaciones_filter = or_(*[Reserva.habitaciones_ids.any(habitacion_id) for habitacion_id in habitacion_ids])
    stmt = select(Reserva).where(habitaciones_filter)

    stmt = stmt.order_by(Reserva.created_at.desc())
    result = await db.execute(stmt)
    reservas = [reserva_to_response(r) for r in result.scalars().all()]
    return ListaReservasHotelResponse(
        total=len(reservas),
        reservas=reservas,
        habitaciones=habitaciones,
    )


@router.get("/{reserva_id}", response_model=ReservaResponse, status_code=status.HTTP_200_OK)
async def obtener_reserva(
    reserva_id: uuid.UUID,
    current_user: User = Depends(get_current_user)
):
    """
    Retorna el detalle de una reserva por su ID.

    En la implementacion real:
    - Consultar PostgreSQL por ID
    - Levantar 404 si no existe
    """
    # TODO: reemplazar con consulta real a la BD
    return ReservaResponse(
        id=reserva_id,
        habitacion_id=uuid.uuid4(),
        fecha_entrada=date(2026, 4, 1),
        fecha_salida=date(2026, 4, 5),
        num_huespedes=2,
        estado=EstadoReserva.confirmada,
        pago_id=None,
        created_at=datetime.now(UTC),
    )
