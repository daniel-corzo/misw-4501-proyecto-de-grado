from passlib.context import CryptContext
from jose import jwt
import datetime
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from travelhub_common.config import BaseAppSettings
from travelhub_common.security import RoleEnum

from app.schemas.auth import RegisterRequest, LoginRequest
from app.models.user import UserCredentials

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, settings: BaseAppSettings):
    to_encode = data.copy()
    expire = datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=settings.jwt_expiration_minutes)
    to_encode.update({"exp": expire})
    
    if not settings.jwt_private_key:
        raise ValueError("JWT private key not configured")
        
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.jwt_private_key, 
        algorithm=settings.jwt_algorithm
    )
    return encoded_jwt

async def register_user(body: RegisterRequest, db: AsyncSession):
    result = await db.execute(select(UserCredentials).where(UserCredentials.email == body.email))
    if result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
        
    hashed_password = get_password_hash(body.password)
    user = UserCredentials(email=body.email, hashed_password=hashed_password, role=body.role)
    if body.id is not None:
        user.id = body.id
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

async def authenticate_user(body: LoginRequest, db: AsyncSession, settings: BaseAppSettings):
    result = await db.execute(select(UserCredentials).where(UserCredentials.email == body.email))
    user = result.scalars().first()

    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales invalidas",
        )

    token_data = {
        "sub": str(user.id),
        "email": user.email,
        "role": user.role.value
    }
    
    return create_access_token(token_data, settings=settings)
