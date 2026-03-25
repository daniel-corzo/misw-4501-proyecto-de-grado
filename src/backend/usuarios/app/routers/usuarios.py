import uuid
import httpx
from datetime import datetime
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.schemas.usuario import CrearUsuarioRequest, ActualizarUsuarioRequest, UsuarioResponse
from app.models.profile import UserProfile
from app.database import get_db
from travelhub_common.security import get_current_user, User, RoleChecker, RoleEnum
from app.config import get_settings, Settings

router = APIRouter(prefix="/usuarios", tags=["usuarios"])


@router.post("", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
async def crear_usuario(
    body: CrearUsuarioRequest,
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings)
):
    """
    Crea un nuevo usuario en el sistema informando al microservicio de auth.
    """
    result = await db.execute(select(UserProfile).where(UserProfile.email == body.email))
    if result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Perfil ya existe con este email",
        )
        
    user_id = body.id if body.id else uuid.uuid4()
    user_profile = UserProfile(
        id=user_id,
        email=body.email,
        nombre=body.nombre,
        apellido=body.apellido,
        telefono=body.telefono,
    )
    await db.add(user_profile)
    await db.flush()

    # Call Auth MS to register the credentials
    async with httpx.AsyncClient(base_url=settings.auth_service_url) as client:
        try:
            auth_response = await client.post(
                "/auth/register",
                json={
                    "id": str(user_id),
                    "email": body.email,
                    "password": body.password,
                    "role": body.role.value
                }
            )
            auth_response.raise_for_status()
        except httpx.HTTPStatusError as e:
            await db.rollback()
            try:
                error_detail = e.response.json().get("detail", "Error en Auth MS")
            except Exception:
                error_detail = "Error de comunicación con Auth MS"
            raise HTTPException(
                status_code=e.response.status_code,
                detail=error_detail
            )
        except httpx.RequestError as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Auth MS no está disponible"
            )

    await db.commit()
    await db.refresh(user_profile)

    return user_profile


@router.get("/me", response_model=UsuarioResponse, status_code=status.HTTP_200_OK)
async def obtener_mi_perfil(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Retorna el propio perfil del usuario autenticado.
    """
    result = await db.execute(select(UserProfile).where(UserProfile.id == current_user.id))
    user_profile = result.scalars().first()
    
    if not user_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Perfil de usuario no encontrado",
        )
    return user_profile

@router.get("/{usuario_id}", response_model=UsuarioResponse, status_code=status.HTTP_200_OK)
async def obtener_usuario(
    usuario_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleChecker([RoleEnum.ADMIN]))
):
    """
    Retorna el perfil de un usuario por su ID. Protegido: Solo Admin.
    """
    result = await db.execute(select(UserProfile).where(UserProfile.id == usuario_id))
    user_profile = result.scalars().first()
    
    if not user_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Perfil de usuario no encontrado",
        )
    return user_profile


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
    if current_user.role != RoleEnum.ADMIN and current_user.id != usuario_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para actualizar este perfil",
        )

    result = await db.execute(select(UserProfile).where(UserProfile.id == usuario_id))
    user_profile = result.scalars().first()
    
    if not user_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Perfil de usuario no encontrado",
        )
        
    if body.nombre is not None:
        user_profile.nombre = body.nombre
    if body.apellido is not None:
        user_profile.apellido = body.apellido
    if body.telefono is not None:
        user_profile.telefono = body.telefono
        
    await db.commit()
    await db.refresh(user_profile)
    
    return user_profile
