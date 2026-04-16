import uuid
from datetime import UTC, datetime, date

from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.reserva import (
    CrearReservaRequest,
    ReservaResponse,
    EstadoReserva,
    ListaReservasResponse,
)
from app.services.reserva_service import crear_reserva_service
from travelhub_common.security import get_current_user, User, RoleEnum

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
        usuario_id=uuid.uuid4(),
        habitacion_id=uuid.uuid4(),
        fecha_entrada=date(2026, 4, 1),
        fecha_salida=date(2026, 4, 5),
        num_huespedes=2,
        estado=EstadoReserva.confirmada,
        pago_id=None,
        created_at=datetime.now(UTC),
    )


@router.get("/usuario/{usuario_id}", response_model=ListaReservasResponse, status_code=status.HTTP_200_OK)
async def listar_reservas_usuario(
    usuario_id: uuid.UUID,
    current_user: User = Depends(get_current_user)
):
    if current_user.role != RoleEnum.ADMIN and current_user.id != usuario_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para ver las reservas de este usuario",
        )
    """
    Lista todas las reservas de un usuario.

    En la implementacion real:
    - Consultar PostgreSQL filtrando por usuario_id
    - Paginar resultados
    """
    # TODO: reemplazar con consulta real a la BD
    return ListaReservasResponse(total=0, reservas=[])
