from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum


class TipoNotificacion(str, Enum):
    reserva_confirmada = "reserva_confirmada"
    reserva_cancelada = "reserva_cancelada"
    pago_aprobado = "pago_aprobado"
    pago_rechazado = "pago_rechazado"
    recordatorio_checkin = "recordatorio_checkin"


class CanalNotificacion(str, Enum):
    email = "email"
    sms = "sms"
    push = "push"


class EnviarNotificacionRequest(BaseModel):
    usuario_id: UUID
    tipo: TipoNotificacion
    canal: CanalNotificacion
    destinatario: str  # email o número de teléfono
    datos: Optional[Dict[str, Any]] = {}  # Variables para la plantilla


class NotificacionResponse(BaseModel):
    id: UUID
    usuario_id: UUID
    tipo: TipoNotificacion
    canal: CanalNotificacion
    destinatario: str
    enviada: bool
    created_at: datetime
