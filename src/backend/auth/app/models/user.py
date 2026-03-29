from uuid import uuid4
from sqlalchemy import Column, String, Enum
from sqlalchemy.dialects.postgresql import UUID
from travelhub_common.models import BaseModel
from travelhub_common.security import RoleEnum

class UserCredentials(BaseModel):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(RoleEnum), default=RoleEnum.USER, nullable=False)
