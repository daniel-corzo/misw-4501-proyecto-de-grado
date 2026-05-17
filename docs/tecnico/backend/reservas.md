# Microservicio: reservas

**Puerto:** 8006  
**Swagger:** http://localhost:8006/docs  
**Responsabilidad:** Ciclo de vida completo de reservas — creación, modificación, confirmación por hotelero, cancelación y consulta por usuario o hotel.

## Endpoints

| Método | Ruta | Descripción | Auth requerida |
|---|---|---|---|
| `POST` | `/api/reservas/` | Crear nueva reserva | Sí |
| `GET` | `/api/reservas/` | Listar reservas del usuario autenticado (por estado) | Sí |
| `GET` | `/api/reservas/{reserva_id}` | Obtener detalle de una reserva | Sí |
| `PATCH` | `/api/reservas/{reserva_id}` | Modificar fechas/habitación de una reserva | Sí |
| `PATCH` | `/api/reservas/{reserva_id}/cancelar` | Cancelar una reserva | Sí |
| `GET` | `/api/reservas/hoteles` | Listar reservas del hotel del hotelero | Sí (tipo: hotel) |
| `GET` | `/api/reservas/hoteles/{reserva_id}` | Ver detalle de reserva desde el lado del hotel | Sí (tipo: hotel) |
| `GET` | `/api/reservas/hoteles/reporte-ingresos` | Reporte de ingresos del hotel por mes | Sí (tipo: hotel) |
| `GET` | `/api/reservas/hoteles/reporte-ocupacion` | Reporte de ocupación por mes y por habitación | Sí (tipo: hotel) |
| `PATCH` | `/api/reservas/{reserva_id}/confirmar` | Confirmar una reserva (hotelero) | Sí (tipo: hotel) |
| `PATCH` | `/api/reservas/{reserva_id}/rechazar` | Rechazar una reserva (hotelero) | Sí (tipo: hotel) |
| `GET` | `/api/reservas/usuario/{usuario_id}` | Listar reservas de un usuario específico | Sí |

## Ciclo de vida de una reserva

```
Viajero crea reserva → estado: pendiente
  ├── Hotelero confirma → estado: confirmada
  │     └── Fecha salida pasa → estado: completada
  ├── Hotelero rechaza → estado: cancelada
  └── Viajero cancela → estado: cancelada
```

## Estados

| Estado | Descripción |
|---|---|
| `pendiente` | Reserva creada, esperando acción del hotelero |
| `confirmada` | Aprobada por el hotelero |
| `cancelada` | Cancelada por el viajero o rechazada por el hotelero |
| `completada` | Estadía finalizada |

## Filtros de listado (viajero)

Al llamar `GET /api/reservas/` se puede filtrar por:

| Filtro | Descripción |
|---|---|
| `activas` | Reservas pendientes o confirmadas con fechas futuras |
| `canceladas` | Reservas canceladas |
| `pasadas` | Reservas completadas |

## Crear una reserva — body

```json
{
  "habitacion_id": "uuid",
  "fecha_entrada": "2025-06-01",
  "fecha_salida": "2025-06-05",
  "num_huespedes": 2,
  "pago_id": "uuid"
}
```

- `fecha_salida` debe ser posterior a `fecha_entrada` (validado con Pydantic).
- `pago_id` es opcional en el momento de crear; el pago puede procesarse antes o después.

## Reportes del hotelero

### `GET /api/reservas/hoteles/reporte-ingresos`

Devuelve un desglose de ingresos del hotel por mes:

```json
{
  "nombre_hotel": "Hotel Dann Carlton",
  "ingresos_por_mes": [
    { "anio": 2025, "mes": 6, "total_ingresos": 1500000, "num_pagos": 3 }
  ],
  "total_general": 1500000,
  "total_pagos": 3
}
```

### `GET /api/reservas/hoteles/reporte-ocupacion`

Devuelve la tasa de ocupación del hotel, desglosada por mes y por habitación:

```json
{
  "nombre_hotel": "Hotel Dann Carlton",
  "total_habitaciones": 5,
  "tasa_ocupacion_global": 62.5,
  "ocupacion_por_mes": [
    { "anio": 2025, "mes": 6, "noches_ocupadas": 10, "noches_disponibles": 16, "tasa_ocupacion": 62.5 }
  ],
  "ocupacion_por_habitacion": [
    { "habitacion_id": "uuid", "numero": "101", "capacidad": 2, "noches_ocupadas": 5, "noches_disponibles": 8, "tasa_ocupacion": 62.5 }
  ],
  "noches_ocupadas_totales": 10,
  "noches_disponibles_totales": 16
}
```

Estos datos son la fuente del **reporte PDF** que el hotelero puede descargar desde el panel de partner en el frontend.

---

## Correos de estado de reserva

El servicio envía correos automáticamente al viajero en estos eventos:

| Evento | Disparador |
|---|---|
| Reserva confirmada | Hotelero llama `PATCH /confirmar` |
| Reserva cancelada | Viajero cancela o hotelero rechaza |

Los correos incluyen el resumen de la reserva (hotel, habitación, fechas, huéspedes y total). Si falla el envío SMTP, el cambio de estado ya fue persistido — solo se registra el error en los logs.

## Dependencias

- PostgreSQL: persistencia de reservas
- SMTP: envío de correos de estado (variables `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS`, `SMTP_FROM_EMAIL`)
