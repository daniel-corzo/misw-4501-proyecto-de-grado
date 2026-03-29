from enum import Enum
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime, time
from typing import List, Optional


class AmenidadHotel(str, Enum):
    pool = "Pool"
    gym = "Gym"
    spa = "Spa"
    restaurant = "Restaurant"
    bar = "Bar"
    wifi = "Wi-Fi"
    parking = "Parking"
    airConditioning = "Air Conditioning"
    roomService = "Room Service"
    laundry = "Laundry"
    concierge = "Concierge"
    beachAccess = "Beach Access"
    skiAccess = "Ski Access"
    petFriendly = "Pet Friendly"
    smokingArea = "Smoking Area"
    evCharging = "EV Charging"
    businessCenter = "Business Center"
    conferenceRoom = "Conference Room"
    childrenPlayground = "Children Playground"
    shuttle = "Shuttle Service"
    breakfastIncluded = "Breakfast Included"


class CrearPoliticaRequest(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    tipo: str
    penalizacion: int
    dias_antelacion: int


class CrearHabitacionRequest(BaseModel):
    capacidad: int
    numero: int
    descripcion: Optional[str] = None
    imagenes: List[str] = Field(default_factory=list)
    monto: int
    impuestos: int
    disponible: bool = True


class CrearHotelRequest(BaseModel):
    nombre: str
    direccion: str
    pais: str
    estado: str
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
    politicas: Optional[List[CrearPoliticaRequest]] = None
    habitaciones: Optional[List[CrearHabitacionRequest]] = None


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
    numero: int
    descripcion: Optional[str] = None
    imagenes: List[str] = Field(default_factory=list)
    monto: int
    impuestos: int
    disponible: bool


class HotelDetalleResponse(BaseModel):
    id: UUID
    nombre: str
    direccion: str
    pais: str
    estado: str
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
