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
Cliente → POST /api/auth/login
       ← { access_token, token_type, expires_in }

Cliente → GET /api/... con header: Authorization: Bearer <access_token>
       ← respuesta normal

# Endpoint de refresh definido (actualmente sin implementación):
Cliente → POST /api/auth/refresh con { refresh_token }
       ← 501 Not Implemented
```

### Tokens y sesión

- `access_token`: vida corta (minutos), usado en cada petición.
- `refresh_token`: previsto para renovar el `access_token` cuando se implemente `POST /api/auth/refresh`.
- `POST /api/auth/logout` invalida la sesión en el servidor.

### Guards en el frontend Angular

| Guard | Propósito |
|---|---|
| `authGuard` | Bloquea rutas si no hay token válido, redirige a login |
| `roleGuard` | Verifica el rol del usuario (viajero vs. hotelero) |
| `typeGuard` | Verifica el tipo de cuenta (e.g., solo tipo `hotel` puede acceder al panel de partner) |

El `auth.interceptor.ts` adjunta automáticamente el Bearer token a todas las peticiones salientes. El `error.interceptor.ts` limpia la sesión local y redirige a login ante errores 401.

## Secrets en producción

En AWS, todos los secretos (JWT keys, RSA keys, DB URL) viven en **AWS Secrets Manager** y se inyectan al contenedor ECS en tiempo de arranque. Ningún secreto se hardcodea en imágenes Docker ni en el repositorio.

| Secret | Uso |
|---|---|
| `jwt_private_key` | Firma de tokens en el servicio `usuarios` |
| `jwt_public_key` | Verificación en todos los servicios |
| `db_url` | Conexión a RDS Aurora PostgreSQL |
