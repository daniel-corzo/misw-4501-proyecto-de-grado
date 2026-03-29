import uuid
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.auth import LoginRequest, LoginResponse, RefreshRequest, RegisterRequest
from app.services.auth_service import register_user, authenticate_user, revoke_token
from app.database import get_db
from travelhub_common.config import BaseAppSettings

router = APIRouter(prefix="/auth", tags=["auth"])
security_scheme = HTTPBearer(auto_error=False)

def get_settings():
    return BaseAppSettings()

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    body: RegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    user = await register_user(body, db)
    return {"message": "Usuario registrado correctamente", "id": str(user.id)}

@router.post("/login", response_model=LoginResponse, status_code=status.HTTP_200_OK)
async def login(
    body: LoginRequest, 
    db: AsyncSession = Depends(get_db),
    settings: BaseAppSettings = Depends(get_settings)
):
    """
    Autentica un usuario y retorna un JWT de acceso.
    """
    access_token = await authenticate_user(body, db, settings)

    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.jwt_expiration_minutes * 60,
    )

@router.post("/refresh", response_model=LoginResponse, status_code=status.HTTP_200_OK)
async def refresh_token(body: RefreshRequest):
    """
    Renueva el token de acceso usando el refresh token.
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Aun no implementado",
    )


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
    db: AsyncSession = Depends(get_db),
    settings: BaseAppSettings = Depends(get_settings),
):
    """
    Invalida el token de acceso actual.
    """
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No autenticado")
    token = credentials.credentials
    try:
        if not settings.jwt_public_key:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="La clave publica JWT no esta configurada")
        jwt.decode(token, settings.jwt_public_key, algorithms=[settings.jwt_algorithm])
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalido")

    await revoke_token(token, db)
    return {"message": "Sesion cerrada correctamente"}
