from pydantic import BaseModel
from uuid import UUID
from datetime import date
from typing import List, Optional
from enum import Enum


class TipoHabitacion(str, Enum):
    sencilla = "sencilla"
    doble = "doble"
    suite = "suite"
    familiar = "familiar"


class HabitacionResponse(BaseModel):
    id: UUID
    hotel_id: UUID
    numero: str
    tipo: TipoHabitacion
    capacidad: int
    precio_noche: float
    disponible: bool


class DisponibilidadRequest(BaseModel):
    fecha_entrada: date
    fecha_salida: date


class ActualizarDisponibilidadRequest(BaseModel):
    disponible: bool
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None


class ListaHabitacionesResponse(BaseModel):
    hotel_id: UUID
    total: int
    habitaciones: List[HabitacionResponse]
