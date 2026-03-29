import uuid
import httpx
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.schemas.usuario import CrearUsuarioRequest, ActualizarUsuarioRequest
from app.models.profile import UserProfile
from travelhub_common.security import User, RoleEnum
from app.config import Settings

async def create_user(body: CrearUsuarioRequest, db: AsyncSession, settings: Settings) -> UserProfile:
    user_id = body.id if body.id else uuid.uuid4()

    result = await db.execute(select(UserProfile).where(UserProfile.id == user_id))
    if result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Perfil ya existe con este id",
        )

    user_profile = UserProfile(
        id=user_id,
        nombre=body.nombre,
        apellido=body.apellido,
        telefono=body.telefono,
    )
    db.add(user_profile)
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
                error_detail = "Error de comunicacion con Auth MS"
            raise HTTPException(
                status_code=e.response.status_code,
                detail=error_detail
            )
        except httpx.RequestError as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Auth MS no esta disponible"
            )

    await db.commit()
    await db.refresh(user_profile)

    return user_profile

async def get_my_profile(current_user: User, db: AsyncSession) -> UserProfile:
    result = await db.execute(select(UserProfile).where(UserProfile.id == current_user.id))
    user_profile = result.scalars().first()
    
    if not user_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Perfil de usuario no encontrado",
        )
    return user_profile

async def get_user_by_id(usuario_id: uuid.UUID, db: AsyncSession) -> UserProfile:
    result = await db.execute(select(UserProfile).where(UserProfile.id == usuario_id))
    user_profile = result.scalars().first()
    
    if not user_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Perfil de usuario no encontrado",
        )
    return user_profile

async def update_user_profile(usuario_id: uuid.UUID, body: ActualizarUsuarioRequest, current_user: User, db: AsyncSession) -> UserProfile:
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
