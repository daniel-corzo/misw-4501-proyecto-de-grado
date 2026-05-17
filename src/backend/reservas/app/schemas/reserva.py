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


class EstadoPagoReserva(str, Enum):
    successful = "successful"
    failed = "failed"


class EstadoPagoDetalle(str, Enum):
    successful = "successful"
    failed = "failed"
    pending = "pending"


class EstadoPagoFiltro(str, Enum):
    successful = "successful"
    failed = "failed"
    pending = "pending"


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
    pago_id: Optional[UUID] = None

    @model_validator(mode="after")
    def al_menos_un_campo(self):
        if not any(
            (
                self.fecha_entrada is not None,
                self.fecha_salida is not None,
                self.num_huespedes is not None,
                self.habitacion_id is not None,
                self.pago_id is not None,
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
    ciudad_hotel: Optional[str] = None
    pais_hotel: Optional[str] = None
    fecha_entrada: date
    fecha_salida: date
    num_huespedes: int
    estado: EstadoReserva
    pago_id: Optional[UUID] = None
    created_at: datetime


class ReservaHotelResponse(ReservaResponse):
    nombre_viajero: Optional[str] = None
    email_viajero: Optional[str] = None
    numero_habitacion: Optional[str] = None
    total_noches: int = Field(default=0, ge=0)
    monto_total: Optional[int] = None
    estado_pago: Optional[EstadoPagoReserva] = None


class ViajeroReservaDetalleResponse(BaseModel):
    id: UUID
    nombre: Optional[str] = None
    email: Optional[str] = None


class PagoReservaDetalleResponse(BaseModel):
    id: Optional[UUID] = None
    estado: EstadoPagoDetalle = EstadoPagoDetalle.pending
    monto: Optional[int] = None
    medio_de_pago: Optional[str] = None
    created_at: Optional[datetime] = None
    tarjeta_ultimos_4: Optional[str] = None


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


class ReservaHotelDetalleCompletoResponse(ReservaDetalleResponse):
    viajero: ViajeroReservaDetalleResponse
    pago: PagoReservaDetalleResponse
    total_noches: int = Field(default=0, ge=0)
    monto_total: Optional[int] = None
    qr_checkin_payload: str


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
    nombre_habitacion: Optional[str] = None


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
    reservas: List[ReservaHotelResponse]
    habitaciones: List[HabitacionHotelResponse]


class IngresoMensualResponse(BaseModel):
    anio: int
    mes: int
    total_pagos: int
    ingresos_totales: int


class ReporteIngresosResponse(BaseModel):
    nombre_hotel: Optional[str]
    ingresos_por_mes: List[IngresoMensualResponse]
    total_general: int
    total_pagos: int


class MiHotelResponse(BaseModel):
    id: UUID
    nombre: str
    created_at: datetime


class OcupacionMensualResponse(BaseModel):
    anio: int
    mes: int
    noches_ocupadas: int
    noches_disponibles: int
    tasa_ocupacion: float


class OcupacionHabitacionResponse(BaseModel):
    habitacion_id: UUID
    numero: str
    capacidad: int
    noches_ocupadas: int
    noches_disponibles: int
    tasa_ocupacion: float


class ReporteOcupacionResponse(BaseModel):
    nombre_hotel: Optional[str]
    fecha_registro: Optional[datetime]
    total_habitaciones: int
    ocupacion_por_mes: List[OcupacionMensualResponse]
    ocupacion_por_habitacion: List[OcupacionHabitacionResponse]
    noches_ocupadas_totales: int
    noches_disponibles_totales: int
    tasa_ocupacion_global: float
