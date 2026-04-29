from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.pago import EstadoPago


class PagarRequest(BaseModel):
    """Cuerpo de POST /pagos/pagar."""

    monto: int = Field(ge=1)
    medio_de_pago: str = Field(min_length=1)
    debe_fallar: bool = False
    payload_cifrado: str = Field(min_length=1)


class PagoResponse(BaseModel):
    id: UUID
    monto: int
    medio_de_pago: str
    created_at: datetime
    updated_at: datetime
    estado: EstadoPago
    tarjeta_ultimos_4: str | None = None


class PayloadTarjetaInterno(BaseModel):
    """JSON descifrado (RSA-OAEP) cargado dentro de payload_cifrado."""

    numero: str = Field(min_length=1)
    cvv: str = Field(min_length=1)
    fecha_expiracion: str = Field(min_length=1)

