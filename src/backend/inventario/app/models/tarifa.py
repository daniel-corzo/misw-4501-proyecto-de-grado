from sqlalchemy import Column, DateTime, String, Integer
from travelhub_common.models import BaseModel

class Tarifa(BaseModel):
    __tablename__ = "tarifas"

    monto = Column(Integer, nullable=False, default=0)
    impuestos = Column(Integer, nullable=False, default=0)
    fecha_inicio = Column(DateTime(timezone=True), nullable=False)
    fecha_fin = Column(DateTime(timezone=True), nullable=False)
