# Microservicio: notificaciones

**Puerto:** 8007  
**Swagger:** http://localhost:8007/docs  
**Responsabilidad:** Recepción de eventos desde SQS y envío de notificaciones/alertas a los usuarios. También expone un endpoint para consultar el historial de notificaciones.

## Endpoints

| Método | Ruta | Descripción | Auth requerida |
|---|---|---|---|
| `POST` | `/api/notificaciones/enviar` | Enviar una notificación manualmente | Sí |
| `GET` | `/api/notificaciones/usuario/{usuario_id}` | Listar notificaciones de un usuario | Sí |

## Consumo de SQS

El servicio escucha continuamente la cola `travelhub-queue`. Cuando el microservicio `reservas` publica un evento (reserva creada, confirmada, cancelada), `notificaciones` lo consume y envía la alerta correspondiente al usuario.

### Eventos que generan notificación

| Evento publicado por `reservas` | Notificación enviada |
|---|---|
| Reserva creada | "Tu reserva fue recibida y está pendiente de confirmación" |
| Reserva confirmada | "Tu reserva ha sido confirmada por el hotel" |
| Reserva cancelada | "Tu reserva ha sido cancelada" |
| Reserva rechazada | "El hotel no pudo confirmar tu reserva" |

## Envío manual

El endpoint `POST /api/notificaciones/enviar` permite enviar una notificación directamente sin pasar por la cola SQS. Útil para pruebas o notificaciones ad-hoc desde otros sistemas.

```json
{
  "usuario_id": "uuid",
  "titulo": "Tu reserva está confirmada",
  "mensaje": "El Hotel Dann Carlton confirmó tu reserva del 1 al 5 de junio."
}
```

## Dependencias

- PostgreSQL: historial de notificaciones
- SQS (`travelhub-queue`): fuente principal de eventos
- En local: LocalStack emula SQS en `http://localstack:4566`
