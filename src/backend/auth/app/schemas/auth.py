from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from travelhub_common.security import RoleEnum


class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    id: Optional[UUID] = None
    email: str
    password: str
    role: Optional[RoleEnum] = RoleEnum.USER


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 3600


class RefreshRequest(BaseModel):
    refresh_token: str


class TokenPayload(BaseModel):
    sub: str
    email: str
    exp: int
