# Microservicio: usuarios

**Puerto:** 8002  
**Swagger:** http://localhost:8002/docs  
**Responsabilidad:** Autenticación, registro de usuarios, gestión de perfiles y emisión de tokens JWT.

## Endpoints

### Autenticación

| Método | Ruta | Descripción | Auth requerida |
|---|---|---|---|
| `POST` | `/api/auth/login` | Iniciar sesión, devuelve access token | No |
| `POST` | `/api/auth/refresh` | Renovar access token usando refresh token (pendiente, responde 501) | No |
| `POST` | `/api/auth/logout` | Cerrar sesión (invalida token actual) | Sí |

### Usuarios

| Método | Ruta | Descripción | Auth requerida |
|---|---|---|---|
| `POST` | `/api/usuarios/` | Registrar nuevo usuario | No |
| `GET` | `/api/usuarios/me` | Obtener perfil del usuario autenticado | Sí |
| `GET` | `/api/usuarios/{usuario_id}` | Obtener perfil por ID | Sí |
| `PUT` | `/api/usuarios/{usuario_id}` | Actualizar datos de perfil | Sí |
| `GET` | `/api/usuarios/resumen` | Listado resumido de usuarios (admin) | Sí |

## Flujo de autenticación

```
POST /api/auth/login → verifica credenciales → genera JWT (RS256)
                     → devuelve { access_token, token_type, expires_in }

POST /api/auth/refresh → endpoint definido, implementación pendiente (501)
POST /api/auth/logout  → invalida token actual en servidor
```

## Tipos de usuario

El sistema distingue dos tipos de cuenta:

| Tipo | Descripción |
|---|---|
| `viajero` | Usuario que busca y reserva alojamiento |
| `hotel` | Socio hotelero que gestiona propiedades |

El tipo se establece en el registro y determina qué rutas están disponibles (ver guards en frontend/mobile).

## Tokens JWT

- Algoritmo: RS256 (firma con clave privada, verificación con clave pública)
- `access_token`: vida corta, adjuntado en el header `Authorization: Bearer`
- `refresh_token`: esquema definido para `/api/auth/refresh` (pendiente de implementación)
- La clave privada solo existe en este servicio; la pública se comparte con los demás servicios para verificación

## Dependencias

- PostgreSQL: almacena usuarios y estado de sesiones
- `common/`: librería compartida con utilitarios JWT
