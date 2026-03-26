from sqlalchemy import Column, String, Float
from sqlalchemy.dialects.postgresql import UUID
from travelhub_common.models import BaseModel
from datetime import datetime, timezone

class Pago(BaseModel):
    __tablename__ = "pagos"

    monto = Column(Float, nullable=False, default=0)
    medio_de_pago = Column(String(100), nullable=False)
    estado = Column(String(50), nullable=False)

    # Cross-service reference (no ForeignKey constraint)
    reserva_id = Column(UUID(as_uuid=True), index=True, nullable=False)
