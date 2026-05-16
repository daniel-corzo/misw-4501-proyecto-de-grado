import asyncio
import json
import logging
from uuid import UUID

from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from travelhub_common.booking_email import (
    BookingEmailEvent,
    BookingEmailPayload,
    send_booking_email,
)
from travelhub_common.security import User

from fastapi import HTTPException, status

from app.config import Settings
from app.models.pago import EstadoPago, Pago
from app.schemas.pago import PagarRequest, PayloadTarjetaInterno, PagoResponse
from app.services.crypto_pago import DescifradoTarjetaError, descifrar_payload_rsa_base64, ultimos_cuatro_digitos
from app.services.reserva_service import (
    ReservaDetallePagoError,
    obtener_reserva_detalle_para_pago,
)


logger = logging.getLogger(__name__)


def _pago_to_response(pago: Pago) -> PagoResponse:
    return PagoResponse(
        id=pago.id,
        monto=pago.monto,
        medio_de_pago=pago.medio_de_pago,
        created_at=pago.created_at,
        updated_at=pago.updated_at,
        estado=pago.estado,
        tarjeta_ultimos_4=pago.tarjeta_ultimos_4,
    )


async def registrar_pago_response(
    db: AsyncSession,
    body: PagarRequest,
    settings: Settings,
    authorization_header: str | None = None,
    current_user: User | None = None,
) -> PagoResponse:
    if not settings.pago_rsa_private_key_pem.strip():
        raise HTTPException(status_code=500, detail="Llave RSA de pagos no configurada")

    try:
        raw = descifrar_payload_rsa_base64(settings.pago_rsa_private_key_pem, body.payload_cifrado)
        tarjeta = PayloadTarjetaInterno.model_validate_json(raw.decode("utf-8"))
        ultimos = ultimos_cuatro_digitos(tarjeta.numero)
    except DescifradoTarjetaError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise HTTPException(status_code=400, detail="Datos de tarjeta invalidos") from exc
    except ValidationError as exc:
        raise HTTPException(status_code=400, detail="Datos de tarjeta invalidos") from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    estado = EstadoPago.failed if body.debe_fallar else EstadoPago.successful

    pago = Pago(
        monto=body.monto,
        medio_de_pago=body.medio_de_pago,
        estado=estado,
        tarjeta_ultimos_4=ultimos,
    )
    db.add(pago)
    await db.flush()
    await db.refresh(pago)
    await db.commit()

    pago_response = _pago_to_response(pago)
    if pago_response.estado == EstadoPago.successful and current_user is not None:
        await _enviar_correo_pago_exitoso(
            body=body,
            pago=pago_response,
            settings=settings,
            authorization_header=authorization_header,
            current_user=current_user,
        )

    return pago_response


async def obtener_pago_por_id(db: AsyncSession, pago_id: UUID) -> PagoResponse:
    result = await db.execute(select(Pago).where(Pago.id == pago_id))
    pago = result.scalar_one_or_none()
    if pago is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pago no encontrado")
    return _pago_to_response(pago)


def _normalizar_medio_de_pago(medio_de_pago: str) -> str:
    return medio_de_pago.strip().replace("_", " ")


async def _enviar_correo_pago_exitoso(
    body: PagarRequest,
    pago: PagoResponse,
    settings: Settings,
    authorization_header: str | None,
    current_user: User,
) -> None:
    if body.reserva_id is None:
        logger.warning(
            "Pago %s exitoso sin reserva_id; se omite el comprobante por correo",
            pago.id,
        )
        return

    try:
        reserva = await obtener_reserva_detalle_para_pago(
            authorization_header,
            body.reserva_id,
        )
        if reserva.viajero_id != current_user.id:
            logger.warning(
                "La reserva %s no pertenece al usuario autenticado %s; se omite comprobante de pago",
                reserva.id,
                current_user.id,
            )
            return
        payload = BookingEmailPayload(
            event=BookingEmailEvent.payment_receipt,
            recipient_email=current_user.email,
            hotel_name=reserva.hotel.nombre,
            reservation_id=str(reserva.id),
            reservation_code=reserva.codigo_reserva,
            room_name=reserva.habitacion.nombre,
            room_number=reserva.habitacion.numero,
            check_in=reserva.fecha_entrada,
            check_out=reserva.fecha_salida,
            guest_count=reserva.num_huespedes,
            payment_amount=pago.monto,
            payment_method=_normalizar_medio_de_pago(pago.medio_de_pago),
            payment_date=pago.created_at,
            card_last4=pago.tarjeta_ultimos_4,
            total_amount=pago.monto,
        )
        await asyncio.to_thread(send_booking_email, payload, settings)
    except ReservaDetallePagoError:
        logger.warning(
            "No fue posible obtener detalle válido de la reserva %s para el comprobante del pago %s",
            body.reserva_id,
            pago.id,
        )
    except Exception:
        logger.exception(
            "No fue posible enviar el comprobante de pago %s para la reserva %s",
            pago.id,
            body.reserva_id,
        )
