from datetime import datetime
from uuid import uuid4
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from travelhub_common.models import BaseModel

class UserProfile(BaseModel):
    __tablename__ = "user_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    email = Column(String(255), unique=True, index=True, nullable=False)
    nombre = Column(String(255), nullable=True)
    apellido = Column(String(255), nullable=True)
    telefono = Column(String(50), nullable=True)