from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional
from travelhub_common.security import RoleEnum


class CrearUsuarioRequest(BaseModel):
    id: Optional[UUID] = None
    email: str
    password: str
    role: Optional[RoleEnum] = RoleEnum.USER
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    telefono: Optional[str] = None


class ActualizarUsuarioRequest(BaseModel):
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    telefono: Optional[str] = None


class UsuarioResponse(BaseModel):
    id: UUID
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    telefono: Optional[str] = None
    created_at: datetime
