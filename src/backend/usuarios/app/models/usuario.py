from sqlalchemy import Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.viajero import Viajero
from travelhub_common.models import BaseModel
import enum


class TipoUsuario(enum.Enum):
    VIAJERO = "viajero"
    HOTEL = "hotel"


class Usuario(BaseModel):
    __tablename__ = "usuarios"

    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    hashed_contrasena: Mapped[str] = mapped_column(String(255), nullable=False)
    tipo: Mapped[TipoUsuario] = mapped_column(Enum(TipoUsuario), nullable=False)

    viajero: Mapped[Viajero | None] = relationship(Viajero)
