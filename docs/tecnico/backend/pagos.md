# Microservicio: pagos

**Puerto:** 8008  
**Swagger:** http://localhost:8008/docs  
**Responsabilidad:** Procesamiento de pagos con tarjeta. Recibe el payload cifrado RSA-OAEP desde el cliente, descifra los datos, valida y registra el pago.

## Endpoints

| Método | Ruta | Descripción | Auth requerida |
|---|---|---|---|
| `POST` | `/api/pagos/pagar` | Procesar un pago con tarjeta | Sí |
| `GET` | `/api/pagos/{pago_id}` | Obtener estado de un pago | Sí |

## Flujo de pago

```
1. Cliente cifra el JSON de tarjeta con RSA-OAEP (clave pública del servidor)
2. Cliente codifica el ciphertext en Base64
3. POST /api/pagos/pagar con { payload_cifrado, reserva_id }
4. El servicio descifra con la clave privada RSA (PAGO_RSA_PRIVATE_KEY_PEM)
5. Valida los datos de tarjeta
6. Registra el pago con los últimos 4 dígitos (nunca el número completo)
7. Devuelve { pago_id, estado, ultimos_cuatro }
8. Si el pago es exitoso, envía un comprobante por correo al viajero
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
  "payload_cifrado": "<Base64 del ciphertext RSA-OAEP>",
  "reserva_id": "uuid"
}
```

El JSON cifrado dentro del `payload_cifrado` tiene la forma:

```json
{
  "numero_tarjeta": "4111111111111111",
  "cvv": "123",
  "fecha_expiracion": "12/26",
  "nombre_titular": "Juan Pérez"
}
```

## Algoritmo de cifrado

| Parámetro | Valor |
|---|---|
| Algoritmo | RSA-OAEP |
| Hash principal | SHA-256 |
| MGF | MGF1-SHA256 |
| Formato de clave privada | PEM tradicional OpenSSL (`BEGIN RSA PRIVATE KEY`) |
| Codificación del ciphertext | Base64 |

## Datos almacenados

El servicio **nunca** almacena el número completo de tarjeta ni el CVV. Solo persiste:
- `pago_id` (UUID)
- `reserva_id`
- `ultimos_cuatro` (últimos 4 dígitos del número)
- `estado` del pago
- Timestamp

## Configuración requerida

La variable de entorno `PAGO_RSA_PRIVATE_KEY_PEM` debe contener la clave privada RSA en formato PEM. En producción, se obtiene de AWS Secrets Manager.

Si esta variable no está configurada, el servicio devuelve `HTTP 500` al intentar procesar cualquier pago.

## Dependencias

- PostgreSQL: registro de pagos
- `PAGO_RSA_PRIVATE_KEY_PEM`: clave privada para descifrado (distinta a las claves JWT)
- SMTP: envío del comprobante de pago (variables `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS`, `SMTP_FROM_EMAIL`)
- Microservicio `reservas`: para obtener los datos de la reserva antes de armar el correo
