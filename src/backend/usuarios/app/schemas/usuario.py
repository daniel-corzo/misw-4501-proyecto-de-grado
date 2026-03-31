from pydantic import BaseModel, ConfigDict, EmailStr, field_validator
from uuid import UUID
from datetime import datetime
from typing import Optional
import re
from app.models.usuario import TipoUsuario
from travelhub_common.security import RoleEnum


class CrearUsuarioRequest(BaseModel):
    email: EmailStr
    password: str
    role: Optional[RoleEnum] = RoleEnum.USER
    nombre: str
    telefono: str
    tipo: TipoUsuario

    @field_validator('password')
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError('La contraseña debe tener mínimo 8 caracteres')
        if not re.search(r'[A-Z]', v):
            raise ValueError('La contraseña debe tener al menos una letra mayúscula')
        if not re.search(r'[a-z]', v):
            raise ValueError('La contraseña debe tener al menos una letra minúscula')
        if not re.search(r'[^a-zA-Z0-9]', v):
            raise ValueError('La contraseña debe tener al menos un carácter especial')
        return v


class ActualizarUsuarioRequest(BaseModel):
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    telefono: Optional[str] = None


class ViajeroResponse(BaseModel):
    id: UUID
    nombre: str
    contacto: str

    model_config = ConfigDict(from_attributes=True)


class UsuarioResponse(BaseModel):
    id: UUID
    tipo: TipoUsuario
    email: str
    role: RoleEnum
    viajero: Optional[ViajeroResponse]

    model_config = ConfigDict(from_attributes=True)
