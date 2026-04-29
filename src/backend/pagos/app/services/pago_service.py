import json
from uuid import UUID

from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import HTTPException, status

from app.config import Settings
from app.models.pago import EstadoPago, Pago
from app.schemas.pago import PagarRequest, PayloadTarjetaInterno, PagoResponse
from app.services.crypto_pago import DecifradoTarjetaError, descifrar_payload_rsa_base64, ultimos_cuatro_digitos


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
) -> PagoResponse:
    if not settings.pago_rsa_private_key_pem.strip():
        raise HTTPException(status_code=500, detail="Llave RSA de pagos no configurada")

    try:
        raw = descifrar_payload_rsa_base64(settings.pago_rsa_private_key_pem, body.payload_cifrado)
        tarjeta = PayloadTarjetaInterno.model_validate_json(raw.decode("utf-8"))
        ultimos = ultimos_cuatro_digitos(tarjeta.numero)
    except DecifradoTarjetaError as exc:
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
        medio_de_pago=body.medio_de_pago.strip(),
        estado=estado,
        tarjeta_ultimos_4=ultimos,
    )
    db.add(pago)
    await db.flush()
    await db.refresh(pago)
    await db.commit()

    return _pago_to_response(pago)


async def obtener_pago_por_id(db: AsyncSession, pago_id: UUID) -> PagoResponse:
    result = await db.execute(select(Pago).where(Pago.id == pago_id))
    pago = result.scalar_one_or_none()
    if pago is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pago no encontrado")
    return _pago_to_response(pago)

