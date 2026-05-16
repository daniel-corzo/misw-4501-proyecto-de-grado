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

## Eventos SQS

Al crear, confirmar o cancelar una reserva, este servicio publica un evento en la cola SQS `travelhub-queue`. El microservicio `notificaciones` consume esa cola y envía la alerta correspondiente al usuario.

## Dependencias

- PostgreSQL: persistencia de reservas
- SQS: publicación de eventos hacia `notificaciones`
