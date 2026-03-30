from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings, get_settings
from app.database import get_db
from app.schemas.auth import LoginRequest, LoginResponse, RefreshRequest
from app.services.auth_service import authenticate_user, revoke_token

router = APIRouter(prefix="/auth", tags=["auth"])
security_scheme = HTTPBearer(auto_error=False)


@router.post("/login", response_model=LoginResponse, status_code=status.HTTP_200_OK)
async def login(
    body: LoginRequest,
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
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
    settings: Settings = Depends(get_settings),
):
    """
    Invalida el token de acceso actual.
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="No autenticado"
        )
    token = credentials.credentials
    try:
        if not settings.jwt_public_key:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="La clave publica JWT no esta configurada",
            )
        jwt.decode(
            token, settings.jwt_public_key, algorithms=[settings.jwt_algorithm]
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalido"
        )

    await revoke_token(token, db)
    return {"message": "Sesion cerrada correctamente"}
