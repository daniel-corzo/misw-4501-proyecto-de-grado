from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional


class CrearUsuarioRequest(BaseModel):
    nombre: str
    apellido: str
    email: str
    password: str
    telefono: Optional[str] = None


class ActualizarUsuarioRequest(BaseModel):
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    telefono: Optional[str] = None


class UsuarioResponse(BaseModel):
    id: UUID
    nombre: str
    apellido: str
    email: str
    telefono: Optional[str]
    created_at: datetime
