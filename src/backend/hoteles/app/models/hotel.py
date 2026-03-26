from sqlalchemy import Column, String, ARRAY, Float, Time
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
    ranking = Column(Float, default=0)
    contacto_celular = Column(String(50), nullable=True)
    contacto_email = Column(String(255), nullable=True)
    imagenes = Column(ARRAY(String), default=list)
    check_in = Column(Time, nullable=False)
    check_out = Column(Time, nullable=False)
    valor_minimo_modificacion = Column(Float, default=0)
    
    # Cross-service reference (no ForeignKey constraint)
    usuario_id = Column(UUID(as_uuid=True), index=True, nullable=False)
