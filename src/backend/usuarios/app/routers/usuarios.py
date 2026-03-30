import uuid
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.usuario import CrearUsuarioRequest, ActualizarUsuarioRequest, UsuarioResponse
from app.database import get_db
from travelhub_common.security import get_current_user, User, RoleChecker, RoleEnum
from app.config import get_settings, Settings
from app.services.usuario_service import create_user, get_my_profile, get_user_by_id, update_user_profile

router = APIRouter(prefix="/usuarios", tags=["usuarios"])


@router.post("", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
async def crear_usuario(
    body: CrearUsuarioRequest,
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings)
):
    """
    Registra un nuevo usuario (credenciales y perfil) en el sistema.
    """
    created_user = await create_user(body, db, settings)

    return UsuarioResponse.model_validate(created_user)

@router.get("/me", response_model=UsuarioResponse, status_code=status.HTTP_200_OK)
async def obtener_mi_perfil(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Retorna el propio perfil del usuario autenticado.
    """
    return await get_my_profile(current_user, db)

@router.get("/{usuario_id}", response_model=UsuarioResponse, status_code=status.HTTP_200_OK)
async def obtener_usuario(
    usuario_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleChecker([RoleEnum.ADMIN]))
):
    """
    Retorna el perfil de un usuario por su ID. Protegido: Solo Admin.
    """
    return await get_user_by_id(usuario_id, db)


@router.put("/{usuario_id}", response_model=UsuarioResponse, status_code=status.HTTP_200_OK)
async def actualizar_usuario(
    usuario_id: uuid.UUID, 
    body: ActualizarUsuarioRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Actualiza los datos del perfil de un usuario.
    Regla: O eres admin, o eres tú mismo.
    """
    return await update_user_profile(usuario_id, body, current_user, db)
