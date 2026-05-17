from enum import Enum

from sqlalchemy import Enum as SAEnum, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from travelhub_common.models import BaseModel


class EstadoPago(str, Enum):
    successful = "successful"
    failed = "failed"


class Pago(BaseModel):
    __tablename__ = "pagos"

    monto: Mapped[int] = mapped_column(Integer, nullable=False)
    medio_de_pago: Mapped[str] = mapped_column(String(100), nullable=False)
    estado: Mapped[EstadoPago] = mapped_column(SAEnum(EstadoPago), nullable=False)
    tarjeta_ultimos_4: Mapped[str | None] = mapped_column(String(4), nullable=True)
