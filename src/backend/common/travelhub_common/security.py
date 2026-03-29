from enum import Enum
from typing import List, Optional
from uuid import UUID
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from pydantic import BaseModel
from .config import BaseAppSettings

security_scheme = HTTPBearer()

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

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    settings: BaseAppSettings = Depends(get_settings)
) -> User:
    try:
        if not settings.jwt_public_key:
            raise HTTPException(status_code=500, detail="La clave publica JWT no esta configurada")
            
        payload = jwt.decode(
            credentials.credentials,
            settings.jwt_public_key,
            algorithms=[settings.jwt_algorithm]
        )
        token_data = TokenPayload(**payload)
        return User(id=UUID(token_data.sub), email=token_data.email, role=token_data.role)
    except JWTError:
        raise HTTPException(status_code=401, detail="No se pudieron validar las credenciales")
    except ValueError:
        raise HTTPException(status_code=401, detail="Subject invalido")

class RoleChecker:
    def __init__(self, allowed_roles: List[RoleEnum]):
        self.allowed_roles = allowed_roles

    def __call__(self, user: User = Depends(get_current_user)):
        if user.role not in self.allowed_roles:
            raise HTTPException(status_code=403, detail="Operacion no permitida")
        return user
