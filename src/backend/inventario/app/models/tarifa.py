from sqlalchemy import Column, String, Integer
from travelhub_common.models import BaseModel

class Tarifa(BaseModel):
    __tablename__ = "tarifas"

    monto = Column(Integer, nullable=False, default=0)
    impuestos = Column(Integer, nullable=False, default=0)
    fechaInicio = Column(String(50), nullable=False)
    fechaFin = Column(String(50), nullable=False)
