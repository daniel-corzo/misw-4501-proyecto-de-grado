import uuid
from fastapi import APIRouter, HTTPException, status
from app.schemas.inventario import (
    HabitacionResponse,
    TipoHabitacion,
    ActualizarDisponibilidadRequest,
    ListaHabitacionesResponse,
)

router = APIRouter(prefix="/inventario", tags=["inventario"])


@router.get(
    "/{hotel_id}/habitaciones",
    response_model=ListaHabitacionesResponse,
    status_code=status.HTTP_200_OK,
)
async def listar_habitaciones(hotel_id: uuid.UUID):
    """
    Lista todas las habitaciones de un hotel con su disponibilidad actual.

    En la implementacion real:
    - Consultar PostgreSQL por hotel_id
    - Cachear en Redis (TTL 2 min) para reducir carga en BD
    - Invalidar cache al actualizar disponibilidad
    """
    # TODO: reemplazar con consulta real a la BD + cache Redis
    habitaciones = [
        HabitacionResponse(
            id=uuid.uuid4(),
            hotel_id=hotel_id,
            numero="101",
            tipo=TipoHabitacion.sencilla,
            capacidad=1,
            precio_noche=250_000.0,
            disponible=True,
        ),
        HabitacionResponse(
            id=uuid.uuid4(),
            hotel_id=hotel_id,
            numero="201",
            tipo=TipoHabitacion.doble,
            capacidad=2,
            precio_noche=380_000.0,
            disponible=True,
        ),
        HabitacionResponse(
            id=uuid.uuid4(),
            hotel_id=hotel_id,
            numero="301",
            tipo=TipoHabitacion.suite,
            capacidad=3,
            precio_noche=750_000.0,
            disponible=False,
        ),
    ]
    return ListaHabitacionesResponse(
        hotel_id=hotel_id,
        total=len(habitaciones),
        habitaciones=habitaciones,
    )


@router.put(
    "/habitaciones/{habitacion_id}",
    response_model=HabitacionResponse,
    status_code=status.HTTP_200_OK,
)
async def actualizar_disponibilidad(
    habitacion_id: uuid.UUID,
    body: ActualizarDisponibilidadRequest,
):
    """
    Actualiza la disponibilidad de una habitacion.

    En la implementacion real:
    - Verificar existencia en BD
    - Actualizar registro y cache Redis
    - Publicar evento 'disponibilidad_actualizada' si es necesario
    """
    # TODO: reemplazar con actualizacion real en BD + invalidar cache
    hotel_id = uuid.uuid4()
    return HabitacionResponse(
        id=habitacion_id,
        hotel_id=hotel_id,
        numero="101",
        tipo=TipoHabitacion.sencilla,
        capacidad=1,
        precio_noche=250_000.0,
        disponible=body.disponible,
    )
