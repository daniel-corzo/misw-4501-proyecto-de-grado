# Microservicio: notificaciones

**Puerto:** 8007  
**Swagger:** http://localhost:8007/docs  
**Responsabilidad:** Envío de notificaciones/alertas a los usuarios y consulta del historial.

## Endpoints

| Método | Ruta | Descripción | Auth requerida |
|---|---|---|---|
| `POST` | `/api/notificaciones/enviar` | Enviar una notificación manualmente | Sí |
| `GET` | `/api/notificaciones/usuario/{usuario_id}` | Listar notificaciones de un usuario | Sí |

## Envío de notificaciones

El endpoint `POST /api/notificaciones/enviar` es el mecanismo actual para enviar notificaciones. Recibe directamente los datos de la notificación sin pasar por cola alguna.

```json
{
  "usuario_id": "uuid",
  "titulo": "Tu reserva está confirmada",
  "mensaje": "El Hotel Dann Carlton confirmó tu reserva del 1 al 5 de junio."
}
```

## Dependencias

- PostgreSQL: historial de notificaciones
