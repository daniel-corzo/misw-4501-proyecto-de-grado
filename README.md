# TravelHub

> Plataforma de reservas hoteleras para Latinoamérica
> Universidad de Los Andes — Maestría en Ingeniería de Software (MISO)

## Qué es TravelHub

TravelHub conecta viajeros con más de 1,200 propiedades hoteleras en **6 países**: Colombia, Perú, Ecuador, México, Chile y Argentina. La plataforma permite buscar alojamiento, reservar, pagar en moneda local y gestionar reservas desde web o móvil.

Este repositorio contiene el MVP desarrollado como proyecto de grado.

## Stack

| Capa | Tecnología |
|------|-----------|
| Web | Angular 19 |
| Móvil | SwiftUI (iOS) |
| Backend | FastAPI (Python 3.12) — 5 microservicios |
| Base de datos | PostgreSQL |
| Caché | Redis |
| Cloud | AWS (ECS Fargate, ALB, SQS, RDS Aurora) |
| IaC | Terraform |
| CI/CD | GitHub Actions + AWS CodeBuild / CodeDeploy |

## Estructura del repositorio

```
src/
├── frontend/          # Portal web Angular
├── mobile/ios/        # App iOS nativa
├── backend/           # Microservicios Python
│   ├── common/        # Librería compartida (auth, factory, modelos base)
│   ├── usuarios/      # Autenticación, perfiles, JWT
│   ├── busquedas/     # Motor de búsqueda de alojamiento
│   ├── hoteles/       # Gestión de propiedades y tarifas
│   ├── reservas/      # Procesamiento de reservas
│   └── notificaciones/# Notificaciones y alertas
├── infrastructure/    # Terraform + AWS
└── tests/e2e/         # Pruebas end-to-end
```

## Levantar el proyecto

### Requisitos

- Docker Desktop
- Node.js 18+

### Backend

1. Generar llaves JWT:
   ```bash
   python generate_keys.py
   ```

2. Crear `.env` en la raíz (ver plantilla abajo) y levantar:
   ```bash
   docker-compose up --build
   ```

**Plantilla `.env`:**
```env
ENVIRONMENT=local
POSTGRES_USER=travelhub
POSTGRES_PASSWORD=travelhub
POSTGRES_DB=travelhub
JWT_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----...-----END PRIVATE KEY-----"
JWT_PUBLIC_KEY="-----BEGIN PUBLIC KEY-----...-----END PUBLIC KEY-----"
AWS_REGION=us-east-1
REDIS_URL=redis://redis:6379
SQS_ENDPOINT=http://localstack:4566
SQS_QUEUE_URL=http://localstack:4566/000000000000/travelhub-queue
```

### Frontend

```bash
cd src/frontend
npm install
npx ng serve
```

Web en `http://localhost:4200`

### Puertos

| Servicio | Puerto | Docs |
|----------|--------|------|
| API Gateway (nginx) | 8080 | http://localhost:8080/docs |
| usuarios | 8002 | http://localhost:8002/docs |
| busquedas | 8003 | http://localhost:8003/docs |
| hoteles | 8004 | http://localhost:8004/docs |
| reservas | 8006 | http://localhost:8006/docs |
| notificaciones | 8007 | http://localhost:8007/docs |

El Swagger UI unificado en `http://localhost:8080/docs` agrupa todos los servicios con un dropdown para navegar entre ellos.

![Swagger UI](./assets/images/openapidocs.png)

### Infraestructura (Terraform + AWS)

```bash
aws configure --profile travelhub
```

> **Importante:** El perfil de AWS debe llamarse `travelhub` para que los scripts funcionen correctamente.

```bash
# Aplicar toda la infraestructura
./src/infrastructure/terraform/scripts/apply.sh

# Destruir toda la infraestructura
./src/infrastructure/terraform/scripts/destroy.sh
```

Los scripts se ejecutan desde la raíz del repositorio y aplican/destruyen los stacks en orden de dependencia.

## Equipo

Proyecto de grado — MISW 4501/4502, Universidad de Los Andes. :goat:

| Integrante | GitHub |
|-----------|--------|
| Andrés Donoso | [@afDonosoD](https://github.com/afDonosoD) |
| Juan Avelido | [@ja-avos](https://github.com/ja-avos) |
| Germán Martínez | [@DavidMS73](https://github.com/DavidMS73) |
| Daniel Corzo | [@daniel-corzo](https://github.com/daniel-corzo) |
