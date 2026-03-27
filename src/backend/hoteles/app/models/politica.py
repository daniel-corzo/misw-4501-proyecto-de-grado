from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from travelhub_common.models import BaseModel
from app.models.hotel import Hotel

class Politica(BaseModel):
    __tablename__ = "politicas"

    nombre = Column(String(255), nullable=False)
    descripcion = Column(String, nullable=True)
    tipo = Column(String(50), nullable=False)
    penalizacion = Column(Integer, nullable=False, default=0)
    dias_antelacion = Column(Integer, nullable=False, default=0)
    
    # Internal relationship within the hoteles service
    hotel_id = Column(UUID(as_uuid=True), ForeignKey("hoteles.id"), nullable=False, index=True)

    hotel = relationship(Hotel, backref="politicas")
