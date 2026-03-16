# TravelHub
> Transformación Digital de la Plataforma de Reservas Hoteleras  
> Universidad de Los Andes — MISO — MISW4501/4502

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

## Ambientes

| Ambiente | Propósito |
|---|---|
| STAGING | Réplica de producción para pruebas de carga, E2E y aceptación |
| PRODUCTION | Ambiente live — sin pruebas directas |

## Cómo levantar el proyecto localmente

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
