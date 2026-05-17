from uuid import UUID

import httpx
from fastapi import HTTPException, status
from pydantic import BaseModel, Field

from app.config import get_settings


class UsuarioResumenResponse(BaseModel):
    id: UUID
    nombre: str | None = None
    email: str


class ListaUsuariosResumenResponse(BaseModel):
    usuarios: list[UsuarioResumenResponse] = Field(default_factory=list)


async def obtener_usuarios_resumen_por_ids(
    authorization_header: str | None,
    usuario_ids: list[UUID],
) -> dict[UUID, UsuarioResumenResponse]:
    if not usuario_ids:
        return {}

    if not authorization_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No autorizado",
        )

    settings = get_settings()
    headers = {"Authorization": authorization_header}
    params = [("ids", str(usuario_id)) for usuario_id in usuario_ids]

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{settings.backend_api_url}/usuarios/resumen",
                headers=headers,
                params=params,
            )

            if response.status_code == status.HTTP_404_NOT_FOUND:
                return {}
            if response.status_code != status.HTTP_200_OK:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail="No fue posible obtener la información de los viajeros",
                )

            payload = ListaUsuariosResumenResponse(**response.json())
            return {usuario.id: usuario for usuario in payload.usuarios}
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No fue posible consultar el servicio de usuarios",
        ) from exc