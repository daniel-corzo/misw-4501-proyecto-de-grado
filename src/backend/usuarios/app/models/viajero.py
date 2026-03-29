from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from travelhub_common.models import BaseModel

class Viajero(BaseModel):
    __tablename__ = "viajeros"

    nombre: Mapped[str] = mapped_column(String(255), nullable=False)
    contacto: Mapped[str] = mapped_column(String(255), nullable=True)

    usuario_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False, unique=True
    )
