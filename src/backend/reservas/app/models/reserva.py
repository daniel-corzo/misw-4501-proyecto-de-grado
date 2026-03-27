from sqlalchemy import Column, String, Integer, DateTime, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from travelhub_common.models import BaseModel

class Reserva(BaseModel):
    __tablename__ = "reservas"

    check_in = Column(DateTime(timezone=True), nullable=False)
    check_out = Column(DateTime(timezone=True), nullable=False)
    estado = Column(String(50), nullable=False)
    personas = Column(Integer, nullable=False, default=1)

    # Cross-service references (no ForeignKey constraints)
    viajero_id = Column(UUID(as_uuid=True), index=True, nullable=False)
    habitaciones_ids = Column(ARRAY(UUID(as_uuid=True)), default=list)
