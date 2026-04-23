from enum import Enum
from typing import List, Optional
from uuid import UUID
from datetime import date, datetime, time

from pydantic import BaseModel, Field, model_validator


class EstadoReserva(str, Enum):
    pendiente = "pendiente"
    confirmada = "confirmada"
    cancelada = "cancelada"
    completada = "completada"


class FiltroReservasUsuario(str, Enum):
    activas = "activas"
    canceladas = "canceladas"
    pasadas = "pasadas"


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


class ModificarReservaRequest(BaseModel):
    fecha_entrada: Optional[date] = None
    fecha_salida: Optional[date] = None
    num_huespedes: Optional[int] = Field(default=None, ge=1)
    habitacion_id: Optional[UUID] = None

    @model_validator(mode="after")
    def al_menos_un_campo(self):
        if not any(
            (
                self.fecha_entrada is not None,
                self.fecha_salida is not None,
                self.num_huespedes is not None,
                self.habitacion_id is not None,
            )
        ):
            raise ValueError("Debe indicar al menos un campo a modificar")
        return self


class ReservaResponse(BaseModel):
    id: UUID
    habitacion_id: UUID
    nombre_habitacion: Optional[str] = None
    nombre_hotel: Optional[str] = None
    imagenes_hotel: List[str] = Field(default_factory=list)
    fecha_entrada: date
    fecha_salida: date
    num_huespedes: int
    estado: EstadoReserva
    pago_id: Optional[UUID] = None
    created_at: datetime


class ReservaHotelDetalleResponse(BaseModel):
    id: Optional[UUID] = None
    nombre: str
    direccion: Optional[str] = None
    ciudad: Optional[str] = None
    pais: Optional[str] = None
    estrellas: Optional[int] = None
    ranking: Optional[float] = None
    imagenes: List[str] = Field(default_factory=list)
    contacto_celular: Optional[str] = None
    contacto_email: Optional[str] = None
    check_in: Optional[time] = None
    check_out: Optional[time] = None


class ReservaHabitacionDetalleCompletoResponse(BaseModel):
    id: UUID
    nombre: str
    descripcion: Optional[str] = None
    numero: Optional[str] = None
    capacidad: Optional[int] = None
    imagenes: List[str] = Field(default_factory=list)
    monto: Optional[int] = None
    impuestos: Optional[int] = None


class ReservaDetalleResponse(BaseModel):
    id: UUID
    codigo_reserva: str
    estado: EstadoReserva
    fecha_entrada: date
    fecha_salida: date
    num_huespedes: int
    pago_id: Optional[UUID] = None
    created_at: datetime
    hotel: ReservaHotelDetalleResponse
    habitacion: ReservaHabitacionDetalleCompletoResponse
    amenidades_hotel: List[str] = Field(default_factory=list)


class ListaReservasResponse(BaseModel):
    total: int
    reservas: List[ReservaResponse]


class HabitacionHotelResponse(BaseModel):
    id: UUID
    capacidad: int
    numero: str
    descripcion: Optional[str] = None
    imagenes: List[str] = Field(default_factory=list)
    monto: int
    impuestos: int
    disponible: bool


class HabitacionReservaDetalleResponse(BaseModel):
    id: UUID
    nombre_habitacion: str
    nombre_hotel: str
    imagenes_hotel: List[str] = Field(default_factory=list)
    hotel_id: Optional[UUID] = None
    direccion_hotel: Optional[str] = None
    ciudad_hotel: Optional[str] = None
    pais_hotel: Optional[str] = None
    estrellas_hotel: Optional[int] = None
    ranking_hotel: Optional[float] = None
    contacto_celular_hotel: Optional[str] = None
    contacto_email_hotel: Optional[str] = None
    check_in_hotel: Optional[time] = None
    check_out_hotel: Optional[time] = None
    amenidades_hotel: List[str] = Field(default_factory=list)
    capacidad_habitacion: Optional[int] = None
    numero_habitacion: Optional[str] = None
    descripcion_habitacion: Optional[str] = None
    imagenes_habitacion: List[str] = Field(default_factory=list)
    monto_habitacion: Optional[int] = None
    impuestos_habitacion: Optional[int] = None


class ListaReservasHotelResponse(BaseModel):
    total: int
    reservas: List[ReservaResponse]
    habitaciones: List[HabitacionHotelResponse]
