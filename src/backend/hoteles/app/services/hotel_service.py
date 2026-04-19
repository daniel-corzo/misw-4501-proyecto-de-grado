import uuid
from typing import Literal

import httpx

from travelhub_common.security import RoleEnum, get_current_user, User
from app.config import get_settings
from app.database import get_db
from fastapi import Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.habitacion import Habitacion
from app.models.hotel import Hotel
from app.models.politica import Politica
from app.schemas.hotel import (
    AmenidadHotel,
    CrearHotelRequest,
    HabitacionDetalleResponse,
    HabitacionResumenResponse,
    HotelDetalleResponse,
    HotelListItemResponse,
    ListaHabitacionesResumenResponse,
    ListaHotelesResponse,
    PoliticaDetalleResponse,
)


OrdenHoteles = Literal["precio_asc", "precio_desc", "rating_desc"]

AMENIDADES_POPULARES_PERMITIDAS = {
    AmenidadHotel.WIFI,
    AmenidadHotel.POOL,
    AmenidadHotel.PET_FRIENDLY,
    AmenidadHotel.BREAKFAST_INCLUDED,
    AmenidadHotel.PARKING,
}


async def listar_hoteles_service(
    db: AsyncSession,
    limit: int,
    offset: int,
    orden: OrdenHoteles,
    precio_min: float | None,
    precio_max: float | None,
    rango_50_1000: bool,
    estrellas: list[int] | None,
    amenidades_populares: list[AmenidadHotel] | None,
) -> ListaHotelesResponse:
    precio_por_hotel_subquery = (
        select(
            Habitacion.hotel_id.label("hotel_id"),
            func.min(Habitacion.monto).label("precio_minimo"),
        )
        .where(Habitacion.disponible.is_(True))
        .group_by(Habitacion.hotel_id)
        .subquery()
    )

    effective_precio_min = precio_min
    effective_precio_max = precio_max
    if rango_50_1000:
        effective_precio_min = 50 if effective_precio_min is None else max(effective_precio_min, 50)
        effective_precio_max = 1000 if effective_precio_max is None else min(effective_precio_max, 1000)

    if (
        effective_precio_min is not None
        and effective_precio_max is not None
        and effective_precio_min > effective_precio_max
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El rango de precio es invalido: precio_min no puede ser mayor que precio_max",
        )

    base_query = (
        select(Hotel, precio_por_hotel_subquery.c.precio_minimo)
        .join(precio_por_hotel_subquery, precio_por_hotel_subquery.c.hotel_id == Hotel.id)
    )

    if estrellas:
        estrellas_limpias = sorted({estrella for estrella in estrellas if 1 <= estrella <= 5})
        if estrellas_limpias:
            base_query = base_query.where(Hotel.estrellas.in_(estrellas_limpias))

    if amenidades_populares:
        amenidades_no_permitidas = [a.value for a in amenidades_populares if a not in AMENIDADES_POPULARES_PERMITIDAS]
        if amenidades_no_permitidas:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Solo se permiten amenidades populares en el filtro: "
                    "WIFI, POOL, PET_FRIENDLY, BREAKFAST_INCLUDED, PARKING"
                ),
            )
        valores_amenidades = [amenidad.value for amenidad in amenidades_populares]
        base_query = base_query.where(Hotel.amenidades.contains(valores_amenidades))

    if effective_precio_min is not None:
        base_query = base_query.where(precio_por_hotel_subquery.c.precio_minimo >= effective_precio_min)

    if effective_precio_max is not None:
        base_query = base_query.where(precio_por_hotel_subquery.c.precio_minimo <= effective_precio_max)

    if orden == "precio_asc":
        base_query = base_query.order_by(precio_por_hotel_subquery.c.precio_minimo.asc().nullslast())
    elif orden == "precio_desc":
        base_query = base_query.order_by(precio_por_hotel_subquery.c.precio_minimo.desc().nullslast())
    else:
        base_query = base_query.order_by(Hotel.ranking.desc(), Hotel.created_at.desc())

    total_result = await db.execute(select(func.count()).select_from(base_query.order_by(None).subquery()))
    total = total_result.scalar_one()

    hoteles_result = await db.execute(base_query.limit(limit).offset(offset))
    hoteles = hoteles_result.all()

    return ListaHotelesResponse(
        total=total,
        hoteles=[
            HotelListItemResponse(
                id=hotel.id,
                nombre=hotel.nombre,
                ciudad=hotel.ciudad,
                pais=hotel.pais,
                estrellas=hotel.estrellas,
                imagenes=hotel.imagenes or [],
                precio_minimo=int(precio_minimo),
                created_at=hotel.created_at,
            )
            for hotel, precio_minimo in hoteles
        ],
    )


async def obtener_hotel_service(db: AsyncSession, hotel_id):
    result = await db.execute(
        select(Hotel)
        .options(
            selectinload(Hotel.politicas),
            selectinload(Hotel.habitaciones),
        )
        .where(Hotel.id == hotel_id)
    )
    hotel = result.scalar_one_or_none()

    if hotel is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hotel no encontrado",
        )

    return HotelDetalleResponse(
        id=hotel.id,
        nombre=hotel.nombre,
        direccion=hotel.direccion,
        pais=hotel.pais,
        estado=hotel.estado,
        departamento=hotel.departamento,
        ciudad=hotel.ciudad,
        descripcion=hotel.descripcion,
        amenidades=hotel.amenidades or [],
        estrellas=hotel.estrellas,
        ranking=hotel.ranking,
        contacto_celular=hotel.contacto_celular,
        contacto_email=hotel.contacto_email,
        imagenes=hotel.imagenes or [],
        check_in=hotel.check_in,
        check_out=hotel.check_out,
        valor_minimo_modificacion=hotel.valor_minimo_modificacion,
        usuario_id=hotel.usuario_id,
        created_at=hotel.created_at,
        updated_at=hotel.updated_at,
        politicas=[
            PoliticaDetalleResponse(
                id=politica.id,
                nombre=politica.nombre,
                descripcion=politica.descripcion,
                tipo=politica.tipo,
                penalizacion=politica.penalizacion,
                dias_antelacion=politica.dias_antelacion,
            )
            for politica in hotel.politicas
        ],
        habitaciones=[
            HabitacionDetalleResponse(
                id=habitacion.id,
                capacidad=habitacion.capacidad,
                numero=habitacion.numero,
                descripcion=habitacion.descripcion,
                imagenes=habitacion.imagenes or [],
                monto=habitacion.monto,
                impuestos=habitacion.impuestos,
                disponible=habitacion.disponible,
            )
            for habitacion in hotel.habitaciones
        ],
    )


async def crear_hotel_service(db: AsyncSession, body: CrearHotelRequest):

    # Create the user, calling the users service
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{get_settings().backend_api_url}/usuarios",
            json={
                "email": body.email,
                "password": body.password,
                "nombre": body.nombre,
                "telefono": body.contacto_celular,
                "tipo": "hotel",
                "role": RoleEnum.USER.value,
            },
        )

        if response.status_code == 400:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=response.json().get("detail", "Error al crear el usuario para el hotel"),
            )

        if response.status_code != 201:
            try:
                error_detail = response.json().get("detail", "Error desconocido")
            except Exception:
                error_detail = "Error desconocido"
            
            raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear el usuario para el hotel: {error_detail}",
            )

        usuario_data = response.json()
        body.usuario_id = uuid.UUID(usuario_data["id"])


    hotel = Hotel(
        id=uuid.uuid4(),
        nombre=body.nombre,
        direccion=body.direccion,
        pais=body.pais,
        estado=body.estado,
        departamento=body.departamento,
        ciudad=body.ciudad,
        descripcion=body.descripcion,
        amenidades=[amenidad.value for amenidad in body.amenidades],
        estrellas=body.estrellas,
        ranking=body.ranking,
        contacto_celular=body.contacto_celular,
        contacto_email=body.contacto_email,
        imagenes=body.imagenes,
        check_in=body.check_in,
        check_out=body.check_out,
        valor_minimo_modificacion=body.valor_minimo_modificacion,
        usuario_id=body.usuario_id,
    )
    db.add(hotel)
    await db.flush()

    if body.politicas:
        for politica in body.politicas:
            db.add(
                Politica(
                    id=uuid.uuid4(),
                    nombre=politica.nombre,
                    descripcion=politica.descripcion,
                    tipo=politica.tipo,
                    penalizacion=politica.penalizacion,
                    dias_antelacion=politica.dias_antelacion,
                    hotel_id=hotel.id,
                )
            )

    if body.habitaciones:
        for habitacion in body.habitaciones:
            db.add(
                Habitacion(
                    id=uuid.uuid4(),
                    capacidad=habitacion.capacidad,
                    numero=habitacion.numero,
                    descripcion=habitacion.descripcion,
                    imagenes=habitacion.imagenes,
                    monto=habitacion.monto,
                    impuestos=habitacion.impuestos,
                    disponible=habitacion.disponible,
                    hotel_id=hotel.id,
                )
            )

    await db.commit()
    return await obtener_hotel_service(db=db, hotel_id=hotel.id)


async def listar_habitaciones_resumen_por_ids_service(
    db: AsyncSession,
    habitacion_ids: list[uuid.UUID],
) -> ListaHabitacionesResumenResponse:
    if not habitacion_ids:
        return ListaHabitacionesResumenResponse(total=0, habitaciones=[])

    result = await db.execute(
        select(
            Habitacion.id,
            Habitacion.numero,
            Habitacion.descripcion,
            Hotel.nombre.label("nombre_hotel"),
            Hotel.imagenes.label("imagenes_hotel"),
        )
        .join(Hotel, Habitacion.hotel_id == Hotel.id)
        .where(Habitacion.id.in_(habitacion_ids))
    )

    habitaciones = []
    for row in result.all():
        nombre_habitacion = row.descripcion or f"Habitacion {row.numero}"
        habitaciones.append(
            HabitacionResumenResponse(
                id=row.id,
                nombre_habitacion=nombre_habitacion,
                nombre_hotel=row.nombre_hotel,
                imagenes_hotel=row.imagenes_hotel or [],
            )
        )

    return ListaHabitacionesResumenResponse(total=len(habitaciones), habitaciones=habitaciones)

async def get_hotel_by_user(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)) -> Hotel:
    result = await db.execute(select(Hotel).where(Hotel.usuario_id == user.id))
    hotel = result.scalar_one_or_none()
    
    if hotel is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El usuario no tiene un hotel asociado. Por favor contacte a soporte.",
        )
    
    return hotel