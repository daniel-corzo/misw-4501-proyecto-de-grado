from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from travelhub_common.models import BaseModel
from app.models.tarifa import Tarifa

class Habitacion(BaseModel):
    __tablename__ = "habitaciones"

    capacidad = Column(Integer, nullable=False, default=1)
    numero = Column(Integer, nullable=False)
    descripcion = Column(String, nullable=True)
    imagenes = Column(ARRAY(String), default=list)

    # Internal relationship within the inventario service
    tarifa_id = Column(UUID(as_uuid=True), ForeignKey("tarifas.id"), nullable=False, index=True)
    tarifa = relationship(Tarifa, backref="habitaciones")

    # Cross-service reference (no ForeignKey constraint)
    hotel_id = Column(UUID(as_uuid=True), index=True, nullable=False)
