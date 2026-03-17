import uuid
from datetime import datetime
from fastapi import APIRouter, HTTPException, status
from app.schemas.pago import ProcesarPagoRequest, PagoResponse, EstadoPago

router = APIRouter(prefix="/pagos", tags=["pagos"])


@router.post("", response_model=PagoResponse, status_code=status.HTTP_201_CREATED)
async def procesar_pago(body: ProcesarPagoRequest):
    """
    Procesa el pago de una reserva via Stripe.

    En la implementacion real:
    - Confirmar el PaymentIntent con Stripe usando token_pago
    - Persistir resultado en PostgreSQL
    - Publicar evento 'pago_procesado' en SQS para notificaciones y reservas
    """
    # TODO: reemplazar con integracion real de Stripe
    # stripe.PaymentIntent.confirm(body.token_pago, amount=int(body.monto * 100))
    return PagoResponse(
        id=uuid.uuid4(),
        reserva_id=body.reserva_id,
        usuario_id=body.usuario_id,
        monto=body.monto,
        moneda=body.moneda,
        metodo_pago=body.metodo_pago,
        estado=EstadoPago.aprobado,
        referencia_externa=f"pi_{uuid.uuid4().hex[:24]}",
        created_at=datetime.utcnow(),
    )


@router.get("/{pago_id}", response_model=PagoResponse, status_code=status.HTTP_200_OK)
async def obtener_pago(pago_id: uuid.UUID):
    """
    Retorna el estado de un pago por su ID.

    En la implementacion real:
    - Consultar PostgreSQL por ID
    - Opcionalmente sincronizar con Stripe si el estado es pendiente
    - Levantar 404 si no existe
    """
    # TODO: reemplazar con consulta real a la BD
    return PagoResponse(
        id=pago_id,
        reserva_id=uuid.uuid4(),
        usuario_id=uuid.uuid4(),
        monto=1_400_000.0,
        moneda="COP",
        metodo_pago="tarjeta_credito",
        estado=EstadoPago.aprobado,
        referencia_externa=f"pi_{uuid.uuid4().hex[:24]}",
        created_at=datetime.utcnow(),
    )
