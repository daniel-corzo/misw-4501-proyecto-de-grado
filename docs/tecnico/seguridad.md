# Seguridad — TravelHub

## Autenticación con JWT

### Algoritmo y claves

TravelHub usa JWT firmados con RSA (`RS256`). Se generan con el script del repositorio:

```bash
python utils/generate_keys.py
```

Cada ejecución produce un par nuevo:
- `PRIVATE_KEY` → `JWT_PRIVATE_KEY` en `.env` (firma los tokens, vive en el servidor)
- `PUBLIC_KEY` → `JWT_PUBLIC_KEY` en `.env` (verifica tokens, compartida entre servicios)

El secreto nunca sale del servidor. Los servicios solo necesitan la clave pública para validar.

### Flujo de autenticación

```
Cliente → POST /api/usuarios/auth/login
       ← { access_token, refresh_token }

Cliente → GET /api/... con header: Authorization: Bearer <access_token>
       ← respuesta normal

# Cuando el access_token expira:
Cliente → POST /api/usuarios/auth/refresh con { refresh_token }
       ← { access_token nuevo, refresh_token nuevo }
```

### Tokens y sesión

- `access_token`: vida corta (minutos), usado en cada petición.
- `refresh_token`: vida larga, usado solo para renovar el access_token.
- `POST /api/usuarios/auth/logout` invalida la sesión en el servidor.

### Guards en el frontend Angular

| Guard | Propósito |
|---|---|
| `authGuard` | Bloquea rutas si no hay token válido, redirige a login |
| `roleGuard` | Verifica el rol del usuario (viajero vs. hotelero) |
| `typeGuard` | Verifica el tipo de cuenta (e.g., solo tipo `hotel` puede acceder al panel de partner) |

El `auth.interceptor.ts` adjunta automáticamente el Bearer token a todas las peticiones salientes y maneja la renovación transparente del access_token.

## Cifrado de datos de pago — RSA-OAEP

### Por qué se cifra en el cliente

Los datos de tarjeta (número, CVV, fecha de expiración) **nunca viajan en texto plano** por la red. El cliente los cifra antes de enviarlos; el servidor solo puede descifrarlos con su clave privada.

### Algoritmo

- RSA-OAEP con SHA-256 y MGF1-SHA256
- El cliente (web/móvil) usa la **clave pública RSA** para cifrar el JSON de la tarjeta
- El resultado se codifica en Base64 y se envía como `payload_cifrado` en el body del pago
- El servicio `pagos` usa la **clave privada RSA** (`PAGO_RSA_PRIVATE_KEY_PEM`) para descifrar

### Generación de claves de pago

Las claves de pago son **distintas** a las claves JWT. Usar el mismo script pero en una ejecución separada:

```bash
# Segunda ejecución del mismo script — produce un par diferente
python utils/generate_keys.py
```

- `PRIVATE_KEY` de esta ejecución → `PAGO_RSA_PRIVATE_KEY_PEM` en el servidor
- `PUBLIC_KEY` de esta ejecución → distribuir a clientes web/móvil para cifrar

### Formato del payload de pago

```json
{
  "payload_cifrado": "<Base64 del ciphertext RSA-OAEP del siguiente JSON>",
  "reserva_id": "uuid"
}
```

El JSON cifrado contiene:
```json
{
  "numero_tarjeta": "4111111111111111",
  "cvv": "123",
  "fecha_expiracion": "12/26",
  "nombre_titular": "Juan Pérez"
}
```

Solo se persisten los **últimos 4 dígitos** de la tarjeta; el número completo nunca se almacena en base de datos.

## Secrets en producción

En AWS, todos los secretos (JWT keys, RSA keys, DB URL) viven en **AWS Secrets Manager** y se inyectan al contenedor ECS en tiempo de arranque. Ningún secreto se hardcodea en imágenes Docker ni en el repositorio.

| Secret | Uso |
|---|---|
| `jwt_private_key` | Firma de tokens en el servicio `usuarios` |
| `jwt_public_key` | Verificación en todos los servicios |
| `pago_rsa_private_key` | Descifrado de payloads en `pagos` |
| `db_url` | Conexión a RDS Aurora PostgreSQL |
