import uuid
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.schemas.auth import LoginRequest, LoginResponse, RefreshRequest, RegisterRequest
from app.models.user import UserCredentials
from app.services.auth_service import verify_password, create_access_token, get_password_hash
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
    result = await db.execute(select(UserCredentials).where(UserCredentials.email == body.email or UserCredentials.id == body.id))
    if result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already registered"
        )
        
    hashed_password = get_password_hash(body.password)
    user = UserCredentials(email=body.email, hashed_password=hashed_password, role=body.role)
    if body.id is not None:
        user.id = body.id
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
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
    result = await db.execute(select(UserCredentials).where(UserCredentials.email == body.email))
    user = result.scalars().first()

    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales invalidas",
        )

    # Generate token
    token_data = {
        "sub": str(user.id),
        "email": user.email,
        "role": user.role.value
    }
    
    access_token = create_access_token(token_data, settings=settings)

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
