# Desarrollo local — TravelHub

## Requisitos

- Docker Desktop (con Docker Compose v2)
- Node.js 18+ (solo para el frontend Angular)
- Python 3.12+ (solo para el script de generación de claves)
- Xcode 15+ (solo para la app iOS)

## 1. Generar claves

El proyecto necesita dos pares de claves RSA independientes: uno para JWT y otro para el cifrado de pagos.

```bash
# Par 1: JWT
python utils/generate_keys.py
# Copia PRIVATE_KEY → JWT_PRIVATE_KEY
# Copia PUBLIC_KEY  → JWT_PUBLIC_KEY

# Par 2: Pagos (ejecutar el script de nuevo — produce un par diferente)
python utils/generate_keys.py
# Copia PRIVATE_KEY → PAGO_RSA_PRIVATE_KEY_PEM
# Guarda PUBLIC_KEY → para el cliente web/móvil (cifra el payload de tarjeta)
```

> **Importante:** No reutilices el mismo par para JWT y pagos. Son contextos de seguridad distintos.

## 2. Crear el archivo `.env`

Crea un archivo `.env` en la raíz del repositorio con el siguiente contenido:

```env
ENVIRONMENT=local

# Base de datos
POSTGRES_USER=travelhub
POSTGRES_PASSWORD=travelhub
POSTGRES_DB=travelhub

# JWT (par 1)
JWT_PRIVATE_KEY="-----BEGIN RSA PRIVATE KEY-----
...contenido...
-----END RSA PRIVATE KEY-----"
JWT_PUBLIC_KEY="-----BEGIN PUBLIC KEY-----
...contenido...
-----END PUBLIC KEY-----"

# Pagos RSA (par 2)
PAGO_RSA_PRIVATE_KEY_PEM="-----BEGIN RSA PRIVATE KEY-----
...contenido...
-----END RSA PRIVATE KEY-----"

AWS_REGION=us-east-1
REDIS_URL=redis://redis:6379
SQS_ENDPOINT=http://localstack:4566
SQS_QUEUE_URL=http://localstack:4566/000000000000/travelhub-queue

# SMTP (correos de reserva y pago)
# Dejar vacío para deshabilitar el envío de correos en local
SMTP_HOST=
SMTP_PORT=587
SMTP_USER=
SMTP_PASS=
SMTP_FROM_EMAIL=
SMTP_SENDER_NAME=TravelHub
SMTP_USE_TLS=true
FRONTEND_BASE_URL=http://localhost:4200
```

Los valores de las claves pueden ir en formato de una sola línea con `\n` escapados o en bloque multilínea como se muestra arriba.

## 3. Levantar el backend

```bash
docker-compose up --build
```

Esto levanta:
- Los 6 microservicios FastAPI
- PostgreSQL
- Redis
- LocalStack
- nginx como API gateway en el puerto 8080

### Verificar que todo está corriendo

```bash
curl http://localhost:8080/docs       # Swagger unificado
curl http://localhost:8002/health     # usuarios
curl http://localhost:8003/health     # busquedas
curl http://localhost:8004/health     # hoteles
curl http://localhost:8006/health     # reservas
curl http://localhost:8007/health     # notificaciones
curl http://localhost:8008/health     # pagos
```

## 4. Levantar el frontend Angular

```bash
cd src/frontend
npm install
npx ng serve
```

La app web queda disponible en `http://localhost:4200`.

El frontend apunta al backend en `http://localhost:8080` por defecto en el entorno de desarrollo.

## 5. Correr la app iOS

1. Abre `src/mobile/ios/TravelHub/TravelHub.xcodeproj` en Xcode.
2. Selecciona un simulador de iPhone (iOS 17+).
3. Asegúrate de que la URL base del API apunte a `http://localhost:8080` en la configuración de desarrollo.
4. Pulsa `Cmd+R` para compilar y ejecutar.

## Estructura de puertos

| Servicio | Puerto |
|---|---|
| nginx (gateway) | 8080 |
| usuarios | 8002 |
| busquedas | 8003 |
| hoteles | 8004 |
| reservas | 8006 |
| notificaciones | 8007 |
| pagos | 8008 |
| PostgreSQL | 5432 |
| Redis | 6379 |
| LocalStack | 4566 |
| Angular (dev) | 4200 |

## Comandos útiles

```bash
# Ver logs de un servicio específico
docker-compose logs -f hoteles

# Reiniciar un servicio sin reconstruir imagen
docker-compose restart reservas

# Reconstruir solo un servicio
docker-compose up --build hoteles

# Detener todo y eliminar volúmenes (base de datos limpia)
docker-compose down -v

# Ejecutar tests de un microservicio
docker-compose exec usuarios pytest

```

## Solución de problemas comunes

| Problema | Causa probable | Solución |
|---|---|---|
| `JWT decode error` | Claves JWT mal formateadas en `.env` | Verificar que los saltos de línea del PEM están correctos |
| `Pago RSA error` | Clave de pagos no configurada | Revisar `PAGO_RSA_PRIVATE_KEY_PEM` en `.env` |
| Servicio no inicia | Puerto ya en uso | `lsof -i :<puerto>` y matar el proceso |
| Frontend no conecta | CORS o URL incorrecta | Verificar `environment.ts` en el frontend |
