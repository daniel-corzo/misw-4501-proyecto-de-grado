from uuid import UUID

from fastapi import APIRouter, Depends, status

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings, get_settings
from app.database import get_db
from app.schemas.pago import PagarRequest, PagoResponse
from app.services import pago_service
from travelhub_common.security import User, get_current_user

router = APIRouter(prefix="/pagos", tags=["pagos"])


@router.post(
    "/pagar",
    response_model=PagoResponse,
    status_code=status.HTTP_201_CREATED,
)
async def pagar(
    body: PagarRequest,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
    settings: Settings = Depends(get_settings),
):
    """
    Registrar un cobro por tarjeta. El PAN/CVV/exp van en payload_cifrado (RSA-OAEP).
    """
    return await pago_service.registrar_pago_response(db, body, settings)


@router.get(
    "/{pago_id}",
    response_model=PagoResponse,
    status_code=status.HTTP_200_OK,
)
async def obtener_pago(
    pago_id: UUID,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    return await pago_service.obtener_pago_por_id(db, pago_id)
