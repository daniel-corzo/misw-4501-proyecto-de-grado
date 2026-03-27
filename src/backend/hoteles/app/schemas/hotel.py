from enum import Enum
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
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


class CrearHotelRequest(BaseModel):
    nombre: str
    ciudad: str
    direccion: str
    estrellas: int
    descripcion: Optional[str] = None
    amenidades: List[AmenidadHotel] = Field(default_factory=list)


class HotelResponse(BaseModel):
    id: UUID
    nombre: str
    ciudad: str
    direccion: str
    estrellas: int
    descripcion: Optional[str]
    amenidades: List[AmenidadHotel]
    created_at: datetime


class ListaHotelesResponse(BaseModel):
    total: int
    hoteles: List[HotelResponse]
