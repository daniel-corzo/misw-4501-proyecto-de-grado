# Microservicio: hoteles

**Puerto:** 8004  
**Swagger:** http://localhost:8004/docs  
**Responsabilidad:** Gestión del catálogo de propiedades hoteleras y sus habitaciones. CRUD de hoteles para socios hoteleros.

## Endpoints

### Hoteles

| Método | Ruta | Descripción | Auth requerida |
|---|---|---|---|
| `GET` | `/api/hoteles/` | Listar todos los hoteles | Sí |
| `POST` | `/api/hoteles/` | Crear un nuevo hotel | Sí (tipo: hotel) |
| `GET` | `/api/hoteles/{hotel_id}` | Obtener detalle de un hotel | Sí |
| `GET` | `/api/hoteles/paises` | Listar países disponibles | Sí |

### Habitaciones

| Método | Ruta | Descripción | Auth requerida |
|---|---|---|---|
| `POST` | `/api/hoteles/habitaciones` | Crear habitación en el hotel del hotelero autenticado | Sí (tipo: hotel) |
| `GET` | `/api/hoteles/habitaciones` | Listar habitaciones del hotel del hotelero autenticado | Sí |
| `GET` | `/api/hoteles/habitaciones/{habitacion_id}` | Obtener detalle de habitación | Sí |
| `PUT` | `/api/hoteles/habitaciones/{habitacion_id}` | Actualizar habitación | Sí (tipo: hotel) |
| `DELETE` | `/api/hoteles/habitaciones/{habitacion_id}` | Eliminar habitación | Sí (tipo: hotel) |
| `GET` | `/api/hoteles/habitaciones/resumen` | Listado resumido por IDs (uso interno) | Sí |

## Modelo de datos

### Hotel

| Campo | Tipo | Descripción |
|---|---|---|
| `id` | UUID | Identificador único |
| `nombre` | string | Nombre del hotel |
| `ciudad` | string | Ciudad donde se ubica |
| `pais` | string | País |
| `estrellas` | int (1-5) | Clasificación |
| `descripcion` | string | Descripción de la propiedad |
| `imagen_url` | string | URL de imagen principal |
| `propietario_id` | UUID | ID del usuario hotelero propietario |

### Habitación

| Campo | Tipo | Descripción |
|---|---|---|
| `id` | UUID | Identificador único |
| `hotel_id` | UUID | Hotel al que pertenece |
| `tipo` | string | Tipo de habitación (ej. doble, suite) |
| `capacidad` | int | Número máximo de huéspedes |
| `precio_por_noche` | float | Tarifa en moneda local |
| `descripcion` | string | Descripción de la habitación |

## Países soportados

El endpoint `GET /api/hoteles/paises` devuelve los países actualmente disponibles en el catálogo: Colombia, Perú, Ecuador, México, Chile y Argentina.

## Dependencias

- PostgreSQL: catálogo de hoteles y habitaciones
- Solo usuarios de tipo `hotel` pueden crear y editar propiedades
