from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional
from app.models.usuario import TipoUsuario
from travelhub_common.security import RoleEnum


class CrearUsuarioRequest(BaseModel):
    email: str
    password: str
    role: Optional[RoleEnum] = RoleEnum.USER
    nombre: Optional[str] = None
    telefono: Optional[str] = None
    tipo: TipoUsuario


class ActualizarUsuarioRequest(BaseModel):
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    telefono: Optional[str] = None


class ViajeroResponse(BaseModel):
    id: UUID
    nombre: str
    contacto: Optional[str]

    model_config = ConfigDict(from_attributes=True)


class UsuarioResponse(BaseModel):
    id: UUID
    tipo: TipoUsuario
    email: str
    viajero: Optional[ViajeroResponse]

    model_config = ConfigDict(from_attributes=True)
