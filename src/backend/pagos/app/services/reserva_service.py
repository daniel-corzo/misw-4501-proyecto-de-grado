from datetime import date
from uuid import UUID

import httpx
from fastapi import status
from pydantic import BaseModel, ValidationError

from app.config import get_settings


class ReservaDetallePagoError(Exception):
    pass


class ReservaHotelPagoResponse(BaseModel):
    nombre: str


class ReservaHabitacionPagoResponse(BaseModel):
    nombre: str
    numero: str | None = None


class ReservaDetallePagoResponse(BaseModel):
    id: UUID
    viajero_id: UUID
    codigo_reserva: str
    fecha_entrada: date
    fecha_salida: date
    num_huespedes: int
    hotel: ReservaHotelPagoResponse
    habitacion: ReservaHabitacionPagoResponse


async def obtener_reserva_detalle_para_pago(
    authorization_header: str | None,
    reserva_id: UUID,
) -> ReservaDetallePagoResponse:
    if not authorization_header:
        raise ReservaDetallePagoError("No autorizado")

    settings = get_settings()
    headers = {"Authorization": authorization_header}

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{settings.backend_api_url}/reservas/{reserva_id}",
                headers=headers,
            )

        if response.status_code == status.HTTP_404_NOT_FOUND:
            raise ReservaDetallePagoError(
                "Reserva no encontrada para generar el comprobante de pago"
            )
        if response.status_code != status.HTTP_200_OK:
            raise ReservaDetallePagoError(
                "No fue posible obtener el detalle de la reserva para el comprobante de pago"
            )

        return ReservaDetallePagoResponse(**response.json())
    except httpx.RequestError as exc:
        raise ReservaDetallePagoError(
            "No fue posible consultar el servicio de reservas"
        ) from exc
    except ValidationError as exc:
        raise ReservaDetallePagoError(
            "Respuesta inválida al consultar el detalle de la reserva"
        ) from exc
