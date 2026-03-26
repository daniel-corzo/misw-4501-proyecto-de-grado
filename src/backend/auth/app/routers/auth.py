import uuid
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.auth import LoginRequest, LoginResponse, RefreshRequest, RegisterRequest
from app.services.auth_service import register_user, authenticate_user
from app.database import get_db
from travelhub_common.config import BaseAppSettings

router = APIRouter(prefix="/auth", tags=["auth"])

def get_settings():
    return BaseAppSettings()

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    body: RegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    user = await register_user(body, db)
    return {"message": "User registered successfully", "id": str(user.id)}

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
        detail="Not implemented yet",
    )
