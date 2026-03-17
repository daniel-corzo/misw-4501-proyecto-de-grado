from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from enum import Enum


class MetodoPago(str, Enum):
    tarjeta_credito = "tarjeta_credito"
    tarjeta_debito = "tarjeta_debito"
    transferencia = "transferencia"


class EstadoPago(str, Enum):
    pendiente = "pendiente"
    aprobado = "aprobado"
    rechazado = "rechazado"
    reembolsado = "reembolsado"


class ProcesarPagoRequest(BaseModel):
    reserva_id: UUID
    usuario_id: UUID
    monto: float
    moneda: str = "COP"
    metodo_pago: MetodoPago
    token_pago: str  # Token generado por el frontend (Stripe.js)


class PagoResponse(BaseModel):
    id: UUID
    reserva_id: UUID
    usuario_id: UUID
    monto: float
    moneda: str
    metodo_pago: MetodoPago
    estado: EstadoPago
    referencia_externa: str
    created_at: datetime
