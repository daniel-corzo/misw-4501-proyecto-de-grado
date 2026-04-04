from sqlalchemy import Column, String, Float, Time, Enum as SAEnum, Integer
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import relationship
from app.enums.hotel import AmenidadHotel
from travelhub_common.models import BaseModel

class Hotel(BaseModel):
    __tablename__ = "hotel"

    nombre = Column(String(255), nullable=False)
    direccion = Column(String(255), nullable=False)
    pais = Column(String(100), nullable=False)
    estado = Column(String(100), nullable=False)
    departamento = Column(String(100), nullable=False)
    ciudad = Column(String(100), nullable=False)
    descripcion = Column(String, nullable=True)
    amenidades = Column(ARRAY(SAEnum(AmenidadHotel, name="hotel_amenity_enum")), nullable=False, default=list)
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
