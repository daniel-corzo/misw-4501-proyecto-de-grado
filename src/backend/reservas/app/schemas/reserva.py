from pydantic import BaseModel
from uuid import UUID
from datetime import date, datetime
from typing import List, Optional
from enum import Enum


class EstadoReserva(str, Enum):
    pendiente = "pendiente"
    confirmada = "confirmada"
    cancelada = "cancelada"
    completada = "completada"


class CrearReservaRequest(BaseModel):
    usuario_id: UUID
    hotel_id: UUID
    habitacion_id: UUID
    fecha_entrada: date
    fecha_salida: date
    num_huespedes: int
    comentarios: Optional[str] = None


class ReservaResponse(BaseModel):
    id: UUID
    usuario_id: UUID
    hotel_id: UUID
    habitacion_id: UUID
    fecha_entrada: date
    fecha_salida: date
    num_huespedes: int
    estado: EstadoReserva
    total: float
    created_at: datetime


class ListaReservasResponse(BaseModel):
    total: int
    reservas: List[ReservaResponse]
