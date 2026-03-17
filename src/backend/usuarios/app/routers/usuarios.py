import uuid
from datetime import datetime
from fastapi import APIRouter, HTTPException, status
from app.schemas.usuario import CrearUsuarioRequest, ActualizarUsuarioRequest, UsuarioResponse

router = APIRouter(prefix="/usuarios", tags=["usuarios"])


@router.post("", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
async def crear_usuario(body: CrearUsuarioRequest):
    """
    Crea un nuevo usuario en el sistema.

    En la implementacion real:
    - Verificar que el email no este registrado
    - Hashear password con passlib/bcrypt
    - Persistir en PostgreSQL via SQLAlchemy
    - Publicar evento 'usuario_creado' en SQS
    """
    # TODO: reemplazar con persistencia real en BD
    return UsuarioResponse(
        id=uuid.uuid4(),
        nombre=body.nombre,
        apellido=body.apellido,
        email=body.email,
        telefono=body.telefono,
        created_at=datetime.utcnow(),
    )


@router.get("/{usuario_id}", response_model=UsuarioResponse, status_code=status.HTTP_200_OK)
async def obtener_usuario(usuario_id: uuid.UUID):
    """
    Retorna el perfil de un usuario por su ID.

    En la implementacion real:
    - Consultar PostgreSQL por ID
    - Levantar 404 si no existe
    """
    # TODO: reemplazar con consulta real a la BD
    return UsuarioResponse(
        id=usuario_id,
        nombre="Juan",
        apellido="Perez",
        email="juan.perez@example.com",
        telefono="+57 300 123 4567",
        created_at=datetime.utcnow(),
    )


@router.put("/{usuario_id}", response_model=UsuarioResponse, status_code=status.HTTP_200_OK)
async def actualizar_usuario(usuario_id: uuid.UUID, body: ActualizarUsuarioRequest):
    """
    Actualiza los datos del perfil de un usuario.

    En la implementacion real:
    - Buscar usuario en BD
    - Aplicar campos no nulos del body (PATCH semantics)
    - Persistir cambios
    """
    # TODO: reemplazar con actualizacion real en la BD
    return UsuarioResponse(
        id=usuario_id,
        nombre=body.nombre or "Juan",
        apellido=body.apellido or "Perez",
        email="juan.perez@example.com",
        telefono=body.telefono or "+57 300 123 4567",
        created_at=datetime.utcnow(),
    )
