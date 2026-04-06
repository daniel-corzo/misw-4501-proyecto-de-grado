from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import relationship
from travelhub_common.models import BaseModel

from app.models.hotel import Hotel


class Habitacion(BaseModel):
    __tablename__ = "habitacion"

    __table_args__ = (
        UniqueConstraint("hotel_id", "numero", name="uq_habitacion_hotel_numero"),
    )

    capacidad = Column(Integer, nullable=False, default=1)
    numero = Column(String, nullable=False)
    descripcion = Column(String, nullable=True)
    imagenes = Column(ARRAY(String), default=list)
    monto = Column(Integer, nullable=False, default=0)
    impuestos = Column(Integer, nullable=False, default=0)
    disponible = Column(Boolean, nullable=False, default=True)

    hotel_id = Column(
        UUID(as_uuid=True),
        ForeignKey(f"{Hotel.__tablename__}.id"),
        nullable=False,
        index=True,
    )
    hotel = relationship(Hotel, back_populates="habitaciones")
