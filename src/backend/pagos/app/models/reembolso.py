from sqlalchemy import Column, String, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from travelhub_common.models import BaseModel
from app.models.pago import Pago

class Reembolso(BaseModel):
    __tablename__ = "reembolsos"

    monto = Column(Numeric(16, 2), nullable=False, default=0)
    razon = Column(String, nullable=True)
    estado = Column(String(50), nullable=False)

    # Internal relationship within the pagos service
    pago_id = Column(UUID(as_uuid=True), ForeignKey("pagos.id"), nullable=False, index=True)
    pago = relationship(Pago, backref="reembolsos")
