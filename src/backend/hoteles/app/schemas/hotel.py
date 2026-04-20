from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime, time
from typing import List, Optional
from app.enums.hotel import AmenidadHotel


class CrearPoliticaRequest(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    tipo: str
    penalizacion: int
    dias_antelacion: int


class CrearHabitacionRequest(BaseModel):
    capacidad: int
    numero: str
    descripcion: Optional[str] = None
    imagenes: List[str] = Field(default_factory=list)
    monto: int
    impuestos: int
    disponible: bool = True


class CrearHotelRequest(BaseModel):
    nombre: str
    direccion: str
    pais: str
    estado: Optional[str] = None
    departamento: str
    ciudad: str
    descripcion: Optional[str] = None
    amenidades: List[AmenidadHotel] = Field(default_factory=list)
    estrellas: int
    ranking: float = 0
    contacto_celular: Optional[str] = None
    contacto_email: Optional[str] = None
    email: str
    password: str
    imagenes: List[str] = Field(default_factory=list)
    check_in: time
    check_out: time
    valor_minimo_modificacion: float
    politicas: Optional[List[CrearPoliticaRequest]] = None
    habitaciones: Optional[List[CrearHabitacionRequest]] = None
    usuario_id: Optional[UUID] = None


class HotelResponse(BaseModel):
    id: UUID
    nombre: str
    ciudad: str
    pais: str
    estrellas: int
    created_at: datetime


class HotelListItemResponse(BaseModel):
    id: UUID
    nombre: str
    ciudad: str
    pais: str
    estrellas: int
    amenidades: List[str] = Field(default_factory=list)
    imagenes: List[str] = Field(default_factory=list)
    precio_minimo: int
    created_at: datetime


class ListaHotelesResponse(BaseModel):
    total: int
    hoteles: List[HotelListItemResponse]


class PoliticaDetalleResponse(BaseModel):
    id: UUID
    nombre: str
    descripcion: Optional[str] = None
    tipo: str
    penalizacion: int
    dias_antelacion: int


class HabitacionDetalleResponse(BaseModel):
    id: UUID
    capacidad: int
    numero: str
    descripcion: Optional[str] = None
    imagenes: List[str] = Field(default_factory=list)
    monto: int
    impuestos: int
    disponible: bool


class ListaHabitacionesResponse(BaseModel):
    total: int
    habitaciones: List[HabitacionDetalleResponse]


class ListaPaisesResponse(BaseModel):
    paises: List[str]


class HabitacionResumenResponse(BaseModel):
    id: UUID
    nombre_habitacion: str
    nombre_hotel: str
    imagenes_hotel: List[str] = Field(default_factory=list)


class ListaHabitacionesResumenResponse(BaseModel):
    total: int
    habitaciones: List[HabitacionResumenResponse]


class HotelDetalleResponse(BaseModel):
    id: UUID
    nombre: str
    direccion: str
    pais: str
    estado: Optional[str] = None
    departamento: str
    ciudad: str
    descripcion: Optional[str] = None
    amenidades: List[AmenidadHotel] = Field(default_factory=list)
    estrellas: int
    ranking: float
    contacto_celular: Optional[str] = None
    contacto_email: Optional[str] = None
    imagenes: List[str] = Field(default_factory=list)
    check_in: time
    check_out: time
    valor_minimo_modificacion: float
    usuario_id: UUID
    created_at: datetime
    updated_at: datetime
    politicas: List[PoliticaDetalleResponse] = Field(default_factory=list)
    habitaciones: List[HabitacionDetalleResponse] = Field(default_factory=list)
