import enum

from sqlalchemy import UUID, Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.viajero import Viajero
from travelhub_common.models import BaseModel
from travelhub_common.security import RoleEnum


class TipoUsuario(enum.Enum):
    VIAJERO = "viajero"
    HOTEL = "hotel"


class Usuario(BaseModel):
    __tablename__ = "usuario"

    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    hashed_contrasena: Mapped[str] = mapped_column(String(255), nullable=False)
    tipo: Mapped[TipoUsuario] = mapped_column(Enum(TipoUsuario), nullable=False)
    role: Mapped[RoleEnum] = mapped_column(
        Enum(RoleEnum), nullable=False, default=RoleEnum.USER
    )

    viajero: Mapped[Viajero | None] = relationship(Viajero, uselist=False)

    hotel_id: Mapped[UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
