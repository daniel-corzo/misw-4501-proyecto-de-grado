from enum import Enum as PyEnum
from sqlalchemy import Column, String, Float, Time, Enum, Integer
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import relationship
from travelhub_common.models import BaseModel


class AmenidadHotel(str, PyEnum):
    POOL = "POOL"
    GYM = "GYM"
    SPA = "SPA"
    RESTAURANT = "RESTAURANT"
    BAR = "BAR"
    WIFI = "WIFI"
    PARKING = "PARKING"
    AIR_CONDITIONING = "AIR_CONDITIONING"
    ROOM_SERVICE = "ROOM_SERVICE"
    LAUNDRY = "LAUNDRY"
    CONCIERGE = "CONCIERGE"
    BEACH_ACCESS = "BEACH_ACCESS"
    SKI_ACCESS = "SKI_ACCESS"
    PET_FRIENDLY = "PET_FRIENDLY"
    SMOKING_AREA = "SMOKING_AREA"
    EV_CHARGING = "EV_CHARGING"
    BUSINESS_CENTER = "BUSINESS_CENTER"
    CONFERENCE_ROOM = "CONFERENCE_ROOM"
    CHILDREN_PLAYGROUND = "CHILDREN_PLAYGROUND"
    SHUTTLE = "SHUTTLE"
    BREAKFAST_INCLUDED = "BREAKFAST_INCLUDED"

class Hotel(BaseModel):
    __tablename__ = "hotel"

    nombre = Column(String(255), nullable=False)
    direccion = Column(String(255), nullable=False)
    pais = Column(String(100), nullable=False)
    estado = Column(String(100), nullable=False)
    departamento = Column(String(100), nullable=False)
    ciudad = Column(String(100), nullable=False)
    descripcion = Column(String, nullable=True)
    amenidades = Column(ARRAY(Enum(AmenidadHotel, name="hotel_amenity_enum")), nullable=False, default=list)
    estrellas = Column(Integer, nullable=False, default=3)
    ranking = Column(Float, default=0)
    contacto_celular = Column(String(50), nullable=True)
    contacto_email = Column(String(255), nullable=True)
    imagenes = Column(ARRAY(String), default=list)
    check_in = Column(Time, nullable=False)
    check_out = Column(Time, nullable=False)
    valor_minimo_modificacion = Column(Float, default=0)
    
    # Cross-service reference (no ForeignKey constraint)
    usuario_id = Column(UUID(as_uuid=True), index=True, nullable=False)

    politicas = relationship("Politica", back_populates="hotel")
    habitaciones = relationship("Habitacion", back_populates="hotel")
