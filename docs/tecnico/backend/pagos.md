# Microservicio: pagos

**Puerto:** 8008  
**Swagger:** http://localhost:8008/docs  
**Responsabilidad:** Procesamiento de pagos con tarjeta. Recibe el payload cifrado RSA-OAEP desde el cliente, descifra los datos, valida y registra el pago.

## Endpoints

| Método | Ruta | Descripción | Auth requerida |
|---|---|---|---|
| `POST` | `/api/pagos/` | Procesar un pago con tarjeta | Sí |
| `GET` | `/api/pagos/{pago_id}` | Obtener estado de un pago | Sí |

## Flujo de pago

```
1. Cliente cifra el JSON de tarjeta con RSA-OAEP (clave pública del servidor)
2. Cliente codifica el ciphertext en Base64
3. POST /api/pagos/ con { payload_cifrado, reserva_id }
4. El servicio descifra con la clave privada RSA (PAGO_RSA_PRIVATE_KEY_PEM)
5. Valida los datos de tarjeta
6. Registra el pago con los últimos 4 dígitos (nunca el número completo)
7. Devuelve { pago_id, estado, ultimos_cuatro }
```

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
