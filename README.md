# TravelHub
> Transformación Digital de la Plataforma de Reservas Hoteleras  
> Universidad de Los Andes — MISO

## Descripción

TravelHub es una plataforma de reservas hoteleras que conecta viajeros, hoteles y agencias de viaje en 6 países de Latinoamérica. Este repositorio contiene el código fuente del MVP desarrollado como proyecto final de la Maestría en Ingeniería de Software.

## Estructura del Repositorio
```
misw-4501-proyecto-de-grado/
├── src/
│   ├── frontend/          # Portal web (Angular 19)
│   ├── mobile/ios/        # App móvil nativa (SwiftUI)
│   ├── backend/           # Microservicios (FastAPI)
│   ├── infrastructure/    # Infraestructura como código (Terraform + AWS)
│   └── tests/e2e/         # Pruebas end-to-end (Cypress + Cucumber)
├── research/              # Experimentos y validaciones Fase 1
└── .github/               # Templates de issues
```

## Stack Tecnológico

| Componente | Tecnología |
|---|---|
| Frontend Web | Angular 19 |
| App Móvil | SwiftUI (iOS nativo) |
| Backend | FastAPI (Python) |
| Base de datos | PostgreSQL (AWS RDS Aurora) |
| Caché | Redis (AWS ElastiCache) |
| Cloud | AWS (ECS Fargate, ALB, SQS, ECR) |
| IaC | Terraform |
| CI/CD | AWS CodeBuild + CodeDeploy |
| Contenedores | Docker |

## Cómo levantar el proyecto localmente

### Backend (Microservicios con Docker Compose)

#### Requisitos previos
- Docker Desktop corriendo

#### 1. Crear el archivo `.env` en la raíz del proyecto

Estas variables son usadas por `docker compose` para levantar la infraestructura local (PostgreSQL, Redis, LocalStack) y para construir la variable `DB_URL` que se inyecta en cada microservicio.

Genere las llaves de JWT públicas y privadas y reemplace los valores respectivos. Puede utilizar el script de python `generate_keys.py`.
```bash
python generate_keys.py
```

```env
ENVIRONMENT=local
POSTGRES_USER=travelhub
POSTGRES_PASSWORD=travelhub
POSTGRES_DB=travelhub
JWT_SECRET=local-secret-only
JWT_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----...-----END PRIVATE KEY-----"
JWT_PUBLIC_KEY="-----BEGIN PUBLIC KEY-----...-----END PUBLIC KEY-----"
AWS_REGION=us-east-1
REDIS_URL=redis://redis:6379
SQS_ENDPOINT=http://localstack:4566
SQS_QUEUE_URL=http://localstack:4566/000000000000/travelhub-queue
STRIPE_KEY=sk_test_placeholder
```

> **Variables que recibe cada microservicio en runtime:**
>
> | Variable | Local (docker-compose) | Producción (AWS ECS) |
> |---|---|---|
> | `DB_URL` | Construido desde `POSTGRES_*` | AWS Secrets Manager → `travelhub/shared-config` clave `db_url` |
> | `JWT_SECRET` | Desde `.env` directamente | AWS Secrets Manager → `travelhub/shared-config` clave `jwt_secret` |
> | `ENVIRONMENT` | `local` | `production` (inyectado por ECS task definition) |
> | `REDIS_URL` | `redis://redis:6379` | Desde `.env` o variable de entorno |
> | `SQS_ENDPOINT` / `SQS_QUEUE_URL` | LocalStack en `localhost:4566` | AWS SQS (endpoint nativo) |

#### 2. Levantar todos los servicios

```bash
docker-compose up --build
```

#### Puertos de los microservicios

| Servicio | Puerto | Swagger UI |
|---|---|---|
| auth | 8001 | http://localhost:8001/docs |
| usuarios | 8002 | http://localhost:8002/docs |
| busqueda | 8003 | http://localhost:8003/docs |
| hoteles | 8004 | http://localhost:8004/docs |
| inventario | 8005 | http://localhost:8005/docs |
| reservas | 8006 | http://localhost:8006/docs |
| pagos | 8007 | http://localhost:8007/docs |
| notificaciones | 8008 | http://localhost:8008/docs |
|---|---|---|
| api gateway | 8080 | http://localhost:8080/api/{microservicio} |
| api docs | 8080 | http://localhost:8080/docs |


![Open Api Docs](./assets/images/openapidocs.png)
> La URL `/docs` expone un **Swagger UI unificado** con todos los microservicios. Usar el dropdown en la parte superior para cambiar entre servicios.

#### Comandos útiles

```bash
# Ver logs de un servicio
docker-compose logs -f auth

# Reiniciar un servicio sin rebuild
docker-compose restart reservas

# Detener todo
docker-compose down

# Detener y eliminar volúmenes (resetea la BD)
docker-compose down -v
```

---

### Frontend (Angular 19)
```bash
cd src/frontend
npm install
npx ng serve
```
Acceder en: `http://localhost:4200`

### Infraestructura (Terraform + AWS)

Configurar el perfil de AWS:
```bash
aws configure --profile travelhub
```

> [!IMPORTANT]
> El perfil de AWS debe llamarse `travelhub` para que los scripts funcionen correctamente.

Aplicar infraestructura:
```bash
./src/infrastructure/terraform/scripts/apply.sh
```

Destruir infraestructura:
```bash
./src/infrastructure/terraform/scripts/destroy.sh
```
