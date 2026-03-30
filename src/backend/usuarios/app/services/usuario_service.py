import uuid

import bcrypt
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.schemas.usuario import (
    CrearUsuarioRequest,
    ActualizarUsuarioRequest,
)
from app.models.usuario import Usuario
from app.models.usuario import TipoUsuario
from app.models.viajero import Viajero
from travelhub_common.security import RoleEnum
from app.config import Settings


def _get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


async def create_user(
    body: CrearUsuarioRequest, db: AsyncSession, settings: Settings
) -> Usuario:
    result = await db.execute(select(Usuario).where(Usuario.email == body.email))
    if result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario ya existe con este email",
        )

    role = body.role if body.role is not None else RoleEnum.USER
    user = Usuario(
        id=uuid.uuid4(),
        email=body.email,
        hashed_contrasena=_get_password_hash(body.password),
        tipo=body.tipo,
        role=role,
    )

    if body.tipo == TipoUsuario.VIAJERO:
        user.viajero = Viajero(
            id=uuid.uuid4(),
            nombre=body.nombre,
            contacto=body.telefono,
        )

    db.add(user)

    # TODO: Call hoteles to create the hotel profile

    await db.commit()
    await db.refresh(user)
    if user.viajero is not None:
        await db.refresh(user.viajero)

    return user


async def get_my_profile(current_user: Usuario, db: AsyncSession) -> Usuario:
    result = await db.execute(select(Usuario).where(Usuario.id == current_user.id))
    user_profile = result.scalars().first()

    if not user_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Perfil de usuario no encontrado",
        )
    return user_profile


async def get_user_by_id(usuario_id: uuid.UUID, db: AsyncSession) -> Usuario:
    result = await db.execute(select(Usuario).where(Usuario.id == usuario_id))
    user_profile = result.scalars().first()

    if not user_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Perfil de usuario no encontrado",
        )
    return user_profile


async def update_user_profile(
    usuario_id: uuid.UUID,
    body: ActualizarUsuarioRequest,
    current_user: Usuario,
    db: AsyncSession,
) -> Usuario:
    if current_user.role != RoleEnum.ADMIN and current_user.id != usuario_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para actualizar este perfil",
        )

    result = await db.execute(select(Usuario).where(Usuario.id == usuario_id))
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
