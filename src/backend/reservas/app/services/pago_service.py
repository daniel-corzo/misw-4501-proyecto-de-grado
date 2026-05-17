import asyncio
from datetime import datetime
from uuid import UUID

import httpx
from fastapi import HTTPException, status
from pydantic import BaseModel

from app.config import get_settings


class PagoResumenResponse(BaseModel):
    id: UUID
    estado: str
    monto: int | None = None
    medio_de_pago: str | None = None
    created_at: datetime | None = None
    tarjeta_ultimos_4: str | None = None


async def obtener_pagos_por_ids(
    authorization_header: str | None,
    pago_ids: list[UUID],
) -> dict[UUID, PagoResumenResponse]:
    if not pago_ids:
        return {}

    if not authorization_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No autorizado",
        )

    settings = get_settings()
    headers = {"Authorization": authorization_header}

    async def obtener_pago(
        client: httpx.AsyncClient,
        pago_id: UUID,
    ) -> PagoResumenResponse | None:
        response = await client.get(
            f"{settings.backend_api_url}/pagos/{pago_id}",
            headers=headers,
        )

        if response.status_code == status.HTTP_404_NOT_FOUND:
            return None
        if response.status_code != status.HTTP_200_OK:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="No fue posible obtener el estado de los pagos",
            )

        return PagoResumenResponse(**response.json())

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            pagos = await asyncio.gather(
                *(obtener_pago(client, pago_id) for pago_id in pago_ids)
            )
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No fue posible consultar el servicio de pagos",
        ) from exc

    return {pago.id: pago for pago in pagos if pago is not None}