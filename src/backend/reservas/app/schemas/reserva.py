from enum import Enum
from typing import List, Optional
from uuid import UUID
from datetime import date, datetime

from pydantic import BaseModel, Field, model_validator


class EstadoReserva(str, Enum):
    pendiente = "pendiente"
    confirmada = "confirmada"
    cancelada = "cancelada"
    completada = "completada"


class CrearReservaRequest(BaseModel):
    habitacion_id: UUID
    fecha_entrada: date
    fecha_salida: date
    num_huespedes: int = Field(ge=1)
    pago_id: Optional[UUID] = None

    @model_validator(mode="after")
    def fecha_salida_after_entrada(self):
        if self.fecha_salida <= self.fecha_entrada:
            raise ValueError("fecha_salida debe ser posterior a fecha_entrada")
        return self


class ReservaResponse(BaseModel):
    id: UUID
    habitacion_id: UUID
    fecha_entrada: date
    fecha_salida: date
    num_huespedes: int
    estado: EstadoReserva
    pago_id: Optional[UUID] = None
    created_at: datetime


class ListaReservasResponse(BaseModel):
    total: int
    reservas: List[ReservaResponse]
