import uuid
from datetime import datetime
from fastapi import APIRouter, HTTPException, status, Depends
from app.schemas.hotel import CrearHotelRequest, HotelResponse, ListaHotelesResponse
from travelhub_common.security import get_current_user, User, RoleChecker, RoleEnum

router = APIRouter(prefix="/hoteles", tags=["hoteles"])


@router.get("", response_model=ListaHotelesResponse, status_code=status.HTTP_200_OK)
async def listar_hoteles(
    current_user: User = Depends(get_current_user)
):
    """
    Retorna la lista de todos los hoteles registrados.

    En la implementacion real:
    - Paginar resultados (limit/offset)
    - Filtrar por ciudad, categoria, etc.
    - Consultar PostgreSQL via SQLAlchemy
    """
    # TODO: reemplazar con consulta real paginada a la BD
    hoteles = [
        HotelResponse(
            id=uuid.uuid4(),
            nombre="Hotel Gran Colombia",
            ciudad="Bogota",
            direccion="Cra 15 # 93-47",
            estrellas=4,
            descripcion="Hotel boutique en el corazon de Bogota",
            amenidades=["wifi", "piscina", "spa", "restaurante"],
            created_at=datetime.utcnow(),
        ),
        HotelResponse(
            id=uuid.uuid4(),
            nombre="Hotel Andino Royal",
            ciudad="Bogota",
            direccion="Calle 85 # 12-28",
            estrellas=5,
            descripcion="Lujo y confort en la zona rosa",
            amenidades=["wifi", "gym", "bar", "concierge", "valet"],
            created_at=datetime.utcnow(),
        ),
    ]
    return ListaHotelesResponse(total=len(hoteles), hoteles=hoteles)


@router.get("/{hotel_id}", response_model=HotelResponse, status_code=status.HTTP_200_OK)
async def obtener_hotel(
    hotel_id: uuid.UUID,
    current_user: User = Depends(get_current_user)
):
    """
    Retorna el detalle de un hotel por su ID.

    En la implementacion real:
    - Consultar PostgreSQL por primary key
    - Levantar 404 si no existe
    """
    # TODO: reemplazar con consulta real a la BD
    return HotelResponse(
        id=hotel_id,
        nombre="Hotel Gran Colombia",
        ciudad="Bogota",
        direccion="Cra 15 # 93-47",
        estrellas=4,
        descripcion="Hotel boutique en el corazon de Bogota",
        amenidades=["wifi", "piscina", "spa", "restaurante"],
        created_at=datetime.utcnow(),
    )


@router.post("", response_model=HotelResponse, status_code=status.HTTP_201_CREATED)
async def crear_hotel(
    body: CrearHotelRequest,
    current_user: User = Depends(RoleChecker([RoleEnum.ADMIN, RoleEnum.MANAGER]))
):
    """
    Registra un nuevo hotel en el sistema.

    En la implementacion real:
    - Validar que no exista hotel duplicado
    - Persistir en PostgreSQL via SQLAlchemy
    """
    # TODO: reemplazar con persistencia real en BD
    return HotelResponse(
        id=uuid.uuid4(),
        nombre=body.nombre,
        ciudad=body.ciudad,
        direccion=body.direccion,
        estrellas=body.estrellas,
        descripcion=body.descripcion,
        amenidades=body.amenidades,
        created_at=datetime.utcnow(),
    )
