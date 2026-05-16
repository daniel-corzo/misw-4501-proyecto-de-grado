# Backend — Microservicios TravelHub

El backend está compuesto por 6 microservicios FastAPI independientes, cada uno con su propia base de datos lógica, esquema de rutas y responsabilidad de dominio.

## Mapa de servicios

| Servicio | Puerto | Responsabilidad |
|---|---|---|
| [usuarios](usuarios.md) | 8002 | Autenticación, registro, perfiles, JWT |
| [busquedas](busquedas.md) | 8003 | Motor de búsqueda de alojamiento disponible |
| [hoteles](hoteles.md) | 8004 | Gestión de propiedades hoteleras y habitaciones |
| [reservas](reservas.md) | 8006 | Ciclo de vida de reservas (crear, confirmar, cancelar) |
| [notificaciones](notificaciones.md) | 8007 | Alertas y notificaciones vía SQS |
| [pagos](pagos.md) | 8008 | Procesamiento de pagos con cifrado RSA-OAEP |

## Estructura común

Todos los servicios siguen la misma organización interna:

```
src/backend/<servicio>/app/
├── main.py          ← instancia FastAPI, registra routers, middleware CORS
├── config.py        ← variables de entorno (Pydantic Settings)
├── database.py      ← conexión async a PostgreSQL (SQLAlchemy 2.x)
├── models/          ← modelos ORM (SQLAlchemy)
├── schemas/         ← modelos Pydantic (request/response DTOs)
├── routers/         ← endpoints HTTP (FastAPI APIRouter)
└── services/        ← lógica de negocio
```

## Biblioteca común (`common`)

El paquete `src/backend/common/` contiene código compartido entre servicios:

- Autenticación JWT (verificación de tokens)
- Factory de dependencias (get_current_user, etc.)
- Modelos base de SQLAlchemy

Cada microservicio instala `common` como dependencia local.

## Patrones usados

- **Async/await** en todos los endpoints y operaciones de base de datos (SQLAlchemy async + asyncpg)
- **Pydantic v2** para validación de request/response
- **Dependency injection** de FastAPI para base de datos y usuario autenticado
- Esquema de base de datos creado automáticamente al arrancar con `Base.metadata.create_all` (SQLAlchemy)
- Documentación automática con **Swagger UI** — disponible en `http://localhost:8080/docs` (local) y en `https://www.travel-hub.online/docs` (producción)
