from pydantic import BaseModel
from datetime import date
from typing import List, Optional


class BusquedaHotelesRequest(BaseModel):
    ciudad: str
    fecha_entrada: date
    fecha_salida: date
    num_huespedes: int = 1


class HotelResultado(BaseModel):
    id: str
    nombre: str
    ciudad: str
    estrellas: int
    precio_por_noche: float
    habitaciones_disponibles: int
    imagen_url: Optional[str] = None


class BusquedaHotelesResponse(BaseModel):
    total: int
    resultados: List[HotelResultado]
