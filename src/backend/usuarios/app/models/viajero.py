from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from travelhub_common.models import BaseModel
from datetime import datetime, timezone

class Viajero(BaseModel):
    __tablename__ = "viajeros"

    nombre = Column(String(255), nullable=False)
    contacto = Column(String(255), nullable=True)

    # Cross-schema/service reference to UserCredentials id in Auth
    usuario_id = Column(UUID(as_uuid=True), index=True, nullable=False, unique=True)
