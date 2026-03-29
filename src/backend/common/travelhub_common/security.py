from enum import Enum
from typing import Dict, List, Optional
from uuid import UUID
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker
from .config import BaseAppSettings
from .database import get_session_factory

security_scheme = HTTPBearer()

_session_factories: Dict[str, async_sessionmaker] = {}

def _get_cached_session_factory(db_url: str) -> async_sessionmaker:
    if db_url not in _session_factories:
        _session_factories[db_url] = get_session_factory(db_url)
    return _session_factories[db_url]

class RoleEnum(str, Enum):
    ADMIN = "ADMIN"
    USER = "USER"
    MANAGER = "MANAGER"

class TokenPayload(BaseModel):
    sub: str
    email: str
    role: RoleEnum
    exp: Optional[int] = None

class User(BaseModel):
    id: UUID
    email: str
    role: RoleEnum

def get_settings():
    return BaseAppSettings()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    settings: BaseAppSettings = Depends(get_settings)
) -> User:
    token = credentials.credentials
    try:
        if not settings.jwt_public_key:
            raise HTTPException(status_code=500, detail="La clave publica JWT no esta configurada")

        payload = jwt.decode(token, settings.jwt_public_key, algorithms=[settings.jwt_algorithm])
        token_data = TokenPayload(**payload)
    except JWTError:
        raise HTTPException(status_code=401, detail="No se pudieron validar las credenciales")
    except ValueError:
        raise HTTPException(status_code=401, detail="Identificador de usuario invalido")

    try:
        user = User(id=UUID(token_data.sub), email=token_data.email, role=token_data.role)
    except ValueError:
        raise HTTPException(status_code=401, detail="Identificador de usuario invalido")

    factory = _get_cached_session_factory(settings.db_url)
    async with factory() as db:
        result = await db.execute(
            text("SELECT 1 FROM revoked_tokens WHERE token = :token"),
            {"token": token}
        )
        if result.first() is not None:
            raise HTTPException(status_code=401, detail="Token ha sido revocado")

    return user

class RoleChecker:
    def __init__(self, allowed_roles: List[RoleEnum]):
        self.allowed_roles = allowed_roles

    def __call__(self, user: User = Depends(get_current_user)):
        if user.role not in self.allowed_roles:
            raise HTTPException(status_code=403, detail="Operacion no permitida")
        return user
