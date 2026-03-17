from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import List, Optional


class CrearHotelRequest(BaseModel):
    nombre: str
    ciudad: str
    direccion: str
    estrellas: int
    descripcion: Optional[str] = None
    amenidades: List[str] = []


class HotelResponse(BaseModel):
    id: UUID
    nombre: str
    ciudad: str
    direccion: str
    estrellas: int
    descripcion: Optional[str]
    amenidades: List[str]
    created_at: datetime


class ListaHotelesResponse(BaseModel):
    total: int
    hoteles: List[HotelResponse]
