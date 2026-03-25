import uuid
from fastapi import APIRouter, Query, status, Depends
from datetime import date
from app.schemas.busqueda import BusquedaHotelesResponse, HotelResultado
from travelhub_common.security import get_current_user, User

router = APIRouter(prefix="/busqueda", tags=["busqueda"])


@router.get("/hoteles", response_model=BusquedaHotelesResponse, status_code=status.HTTP_200_OK)
async def buscar_hoteles(
    ciudad: str = Query(..., description="Ciudad de destino"),
    fecha_entrada: date = Query(..., description="Fecha de llegada (YYYY-MM-DD)"),
    fecha_salida: date = Query(..., description="Fecha de salida (YYYY-MM-DD)"),
    num_huespedes: int = Query(1, ge=1, le=20, description="Numero de huespedes"),
    estrellas_min: int = Query(1, ge=1, le=5, description="Minimo de estrellas"),
    precio_max: float = Query(None, description="Precio maximo por noche"),
    current_user: User = Depends(get_current_user)
):
    """
    Busca hoteles disponibles segun los criterios indicados.

    En la implementacion real:
    - Consultar indice en PostgreSQL / Elasticsearch
    - Filtrar por disponibilidad via servicio de inventario
    - Cachear resultados frecuentes en Redis (TTL 5 min)
    """
    # TODO: reemplazar con busqueda real contra BD / cache
    resultados = [
        HotelResultado(
            id=str(uuid.uuid4()),
            nombre="Hotel Gran Colombia",
            ciudad=ciudad,
            estrellas=4,
            precio_por_noche=350_000.0,
            habitaciones_disponibles=8,
            imagen_url="https://placehold.co/400x300",
        ),
        HotelResultado(
            id=str(uuid.uuid4()),
            nombre="Hotel Andino Royal",
            ciudad=ciudad,
            estrellas=5,
            precio_por_noche=620_000.0,
            habitaciones_disponibles=3,
            imagen_url="https://placehold.co/400x300",
        ),
    ]

    return BusquedaHotelesResponse(total=len(resultados), resultados=resultados)
