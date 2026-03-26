from sqlalchemy import Column, String, Integer, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from travelhub_common.models import BaseModel

class Hotel(BaseModel):
    __tablename__ = "hoteles"

    nombre = Column(String(255), nullable=False)
    direccion = Column(String(255), nullable=False)
    pais = Column(String(100), nullable=False)
    estado = Column(String(100), nullable=False)
    departamento = Column(String(100), nullable=False)
    ciudad = Column(String(100), nullable=False)
    descripcion = Column(String, nullable=True)
    amenidades = Column(String, nullable=True)
    ranking = Column(Integer, default=0)
    contactoCelular = Column(String(50), nullable=True)
    contactoEmail = Column(String(255), nullable=True)
    images = Column(ARRAY(String), default=[])
    checkInHour = Column(String(10), nullable=False)
    checkOutHour = Column(String(10), nullable=False)
    valorMinimoModificacion = Column(Integer, default=0)
    
    # Cross-service reference (no ForeignKey constraint)
    usuario_id = Column(UUID(as_uuid=True), index=True, nullable=False)
