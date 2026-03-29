import datetime

import bcrypt
from fastapi import HTTPException, status
from jose import jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from travelhub_common.config import BaseAppSettings

from app.models.revoked_token import RevokedToken
from app.models.usuario import Usuario
from app.schemas.auth import LoginRequest


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())


def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def create_access_token(data: dict, settings: BaseAppSettings):
    to_encode = data.copy()
    expire = datetime.datetime.now(datetime.UTC) + datetime.timedelta(
        minutes=settings.jwt_expiration_minutes
    )
    to_encode.update({"exp": expire})

    if not settings.jwt_private_key:
        raise ValueError("La clave privada JWT no esta configurada")

    return jwt.encode(
        to_encode,
        settings.jwt_private_key,
        algorithm=settings.jwt_algorithm,
    )


async def authenticate_user(
    body: LoginRequest, db: AsyncSession, settings: BaseAppSettings
):
    result = await db.execute(select(Usuario).where(Usuario.email == body.email))
    user = result.scalars().first()

    if not user or not verify_password(body.password, user.hashed_contrasena):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales invalidas",
        )

    token_data = {
        "sub": str(user.id),
        "email": user.email,
        "role": user.role.value,
    }

    return create_access_token(token_data, settings=settings)


async def revoke_token(token: str, db: AsyncSession) -> None:
    db.add(RevokedToken(token=token))
    await db.commit()


async def is_token_revoked(token: str, db: AsyncSession) -> bool:
    result = await db.execute(select(RevokedToken).where(RevokedToken.token == token))
    return result.scalars().first() is not None
