import httpx
from fastapi import HTTPException, status

from app.config import get_settings
from app.schemas.reserva import HabitacionHotelResponse


async def obtener_habitaciones_hotel(authorization_header: str | None) -> list[HabitacionHotelResponse]:
    if not authorization_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No autorizado",
        )

    settings = get_settings()
    headers = {"Authorization": authorization_header}
    limit = 100
    offset = 0
    habitaciones: list[HabitacionHotelResponse] = []
    total = None

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            while total is None or len(habitaciones) < total:
                response = await client.get(
                    f"{settings.backend_api_url}/hoteles/habitaciones",
                    headers=headers,
                    params={"limit": limit, "offset": offset},
                )

                if response.status_code == status.HTTP_404_NOT_FOUND:
                    return []
                if response.status_code != status.HTTP_200_OK:
                    raise HTTPException(
                        status_code=status.HTTP_502_BAD_GATEWAY,
                        detail="No fue posible obtener las habitaciones del hotel",
                    )

                payload = response.json()
                total = payload.get("total", 0)
                page_items = payload.get("habitaciones", [])
                habitaciones.extend(
                    HabitacionHotelResponse(**habitacion) for habitacion in page_items
                )

                if not page_items:
                    break
                if len(page_items) < limit:
                    break

                offset += limit
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No fue posible consultar el servicio de hoteles",
        ) from exc

    return habitaciones