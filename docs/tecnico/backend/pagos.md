# Microservicio: pagos

**Puerto:** 8008  
**Swagger:** http://localhost:8008/docs  
**Responsabilidad:** Procesamiento de pagos con tarjeta. Recibe los datos de tarjeta, valida y registra el pago.

## Endpoints

| Método | Ruta | Descripción | Auth requerida |
|---|---|---|---|
| `POST` | `/api/pagos/pagar` | Procesar un pago con tarjeta | Sí |
| `GET` | `/api/pagos/{pago_id}` | Obtener estado de un pago | Sí |

## Flujo de pago

```
1. POST /api/pagos/pagar con { numero, cvv, fecha_expiracion, reserva_id }
2. Valida los datos de tarjeta
3. Registra el pago con los últimos 4 dígitos (nunca el número completo)
4. Devuelve { pago_id, estado, ultimos_cuatro }
5. Si el pago es exitoso, envía un comprobante por correo al viajero
```

## Correo de comprobante de pago

Cuando el pago resulta exitoso, el servicio envía automáticamente un correo al viajero con:

- Código de reserva
- Hotel y habitación
- Fechas de check-in y check-out
- Número de huéspedes
- Monto pagado y medio de pago
- Últimos 4 dígitos de la tarjeta
- Fecha y hora del pago

El correo se envía de forma asíncrona (no bloquea la respuesta del endpoint). Si falla el envío por SMTP, el pago ya fue registrado y no se revierte — solo se registra el error en los logs.

## Body del request

```json
{
  "numero": "4111111111111111",
  "cvv": "123",
  "fecha_expiracion": "12/26",
  "reserva_id": "uuid"
}
```

## Datos almacenados

El servicio **nunca** almacena el número completo de tarjeta ni el CVV. Solo persiste:
- `pago_id` (UUID)
- `reserva_id`
- `ultimos_cuatro` (últimos 4 dígitos del número)
- `estado` del pago
- Timestamp

## Dependencias

- PostgreSQL: registro de pagos
- SMTP: envío del comprobante de pago (variables `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS`, `SMTP_FROM_EMAIL`)
- Microservicio `reservas`: para obtener los datos de la reserva antes de armar el correo
