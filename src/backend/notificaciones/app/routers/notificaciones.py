import uuid
from datetime import datetime
from fastapi import APIRouter, status
from app.schemas.notificacion import EnviarNotificacionRequest, NotificacionResponse

router = APIRouter(prefix="/notificaciones", tags=["notificaciones"])


@router.post("/enviar", response_model=NotificacionResponse, status_code=status.HTTP_201_CREATED)
async def enviar_notificacion(body: EnviarNotificacionRequest):
    """
    Envia una notificacion a un usuario por el canal indicado.

    En la implementacion real:
    - Seleccionar plantilla segun tipo de notificacion
    - Enviar via SES (email) o SNS (SMS) usando boto3
    - Persistir registro de envio (auditoria)
    - Consumir tambien desde cola SQS para procesamiento asincrono
    """
    # TODO: reemplazar con envio real via SES/SNS
    return NotificacionResponse(
        id=uuid.uuid4(),
        usuario_id=body.usuario_id,
        tipo=body.tipo,
        canal=body.canal,
        destinatario=body.destinatario,
        enviada=True,
        created_at=datetime.utcnow(),
    )


@router.get("/usuario/{usuario_id}", response_model=list[NotificacionResponse], status_code=status.HTTP_200_OK)
async def listar_notificaciones_usuario(usuario_id: uuid.UUID):
    """
    Lista el historial de notificaciones enviadas a un usuario.

    En la implementacion real:
    - Consultar tabla de notificaciones filtrando por usuario_id
    - Paginar y ordenar por fecha descendente
    """
    # TODO: reemplazar con consulta real a la BD
    return []
