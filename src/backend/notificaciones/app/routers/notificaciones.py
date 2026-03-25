import uuid
from datetime import datetime
from fastapi import APIRouter, status, Depends, HTTPException
from app.schemas.notificacion import EnviarNotificacionRequest, NotificacionResponse
from travelhub_common.security import get_current_user, User, RoleChecker, RoleEnum

router = APIRouter(prefix="/notificaciones", tags=["notificaciones"])


@router.post("/enviar", response_model=NotificacionResponse, status_code=status.HTTP_201_CREATED)
async def enviar_notificacion(
    body: EnviarNotificacionRequest,
    current_user: User = Depends(RoleChecker([RoleEnum.ADMIN]))
):
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
async def listar_notificaciones_usuario(
    usuario_id: uuid.UUID,
    current_user: User = Depends(get_current_user)
):
    if current_user.role != RoleEnum.ADMIN and current_user.id != usuario_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para ver estas notificaciones",
        )
    """
    Lista el historial de notificaciones enviadas a un usuario.

    En la implementacion real:
    - Consultar tabla de notificaciones filtrando por usuario_id
    - Paginar y ordenar por fecha descendente
    """
    # TODO: reemplazar con consulta real a la BD
    return []
