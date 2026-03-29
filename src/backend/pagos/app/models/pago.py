from sqlalchemy import Column, String, Numeric
from sqlalchemy.dialects.postgresql import UUID
from travelhub_common.models import BaseModel

class Pago(BaseModel):
    __tablename__ = "pagos"

    monto = Column(Numeric(16, 2), nullable=False, default=0)
    medio_de_pago = Column(String(100), nullable=False)
    estado = Column(String(50), nullable=False)

    # Cross-service reference (no ForeignKey constraint)
    reserva_id = Column(UUID(as_uuid=True), index=True, nullable=False)
