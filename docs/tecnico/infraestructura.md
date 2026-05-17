# Infraestructura AWS — TravelHub

## Visión general

TravelHub corre completamente en AWS sobre la región `us-east-1`. La infraestructura se gestiona con Terraform. En CI/CD, frontend usa CodePipeline/CodeBuild y backend usa GitHub Actions para build/push y disparar despliegues Blue/Green con CodeDeploy.

## Componentes principales

### Frontend

| Componente | Descripción |
|---|---|
| S3 Bucket | Almacena los archivos estáticos del build de Angular |
| CloudFront | CDN global, HTTPS, caché de assets |

El build de Angular (`ng build --configuration production`) se sube a S3 y CloudFront lo distribuye. CodePipeline invalida la caché de CloudFront al final de cada despliegue.

### Cómputo (Backend)

| Componente | Descripción |
|---|---|
| ECS Fargate | Cluster serverless — no se gestionan EC2s |
| ALB | Application Load Balancer con routing por path |
| Target Groups | Blue y Green por cada microservicio (para Blue/Green deployments) |
| ECR | Registro Docker privado, un repositorio por microservicio |

Hay 6 servicios ECS, uno por microservicio: `usuarios`, `busquedas`, `hoteles`, `reservas`, `notificaciones` y `pagos`. Cada tarea Fargate corre la imagen Docker del microservicio correspondiente.

### Red (VPC)

- VPC dedicada en `us-east-1`
- 2 Availability Zones con subnets públicas
- El ALB está en las subnets públicas
- Las tareas ECS tienen IPs dentro de la VPC

### Base de datos y caché

| Componente | Descripción |
|---|---|
| RDS Aurora PostgreSQL 15 | `db.t3.micro`, Multi-AZ |
| ElastiCache Redis | Para caché de búsquedas |
| Secrets Manager | JWT keys, RSA keys, DB URL |

## CI/CD

### Pipelines

Hay dos flujos de CI/CD:

- **Frontend**: 1 pipeline de CodePipeline (con CodeBuild) para compilar Angular, publicar en S3 e invalidar CloudFront.
- **Backend**: workflow de GitHub Actions (`backend-build.yml`) con matriz de servicios que compila imágenes, publica en ECR y crea despliegues en CodeDeploy.

### Frontend pipeline

```
GitHub (main) → CodePipeline → CodeBuild (ng build) → S3 sync → CloudFront invalidation
```

### Backend workflow (por microservicio)

```
GitHub (main) → GitHub Actions (docker build + ECR push + nueva task definition ECS) → CodeDeploy (Blue/Green en ECS)
```

### Blue/Green deployment

Cada microservicio tiene dos Target Groups: `-blue` (producción) y `-green` (nueva versión). CodeDeploy despliega en el grupo green, corre health checks, y cambia el tráfico del ALB de blue a green sin downtime.

## Terraform

La infraestructura está organizada en módulos y stacks:

```
src/infrastructure/terraform/
├── environments/     ← variables por entorno (dev, prod)
├── modules/          ← módulos reutilizables (ecs, rds, alb, etc.)
├── scripts/          ← scripts de apply y destroy
└── stacks/           ← composición de módulos por contexto
```

### Aplicar infraestructura

```bash
# Configurar el perfil AWS (debe llamarse 'travelhub')
aws configure --profile travelhub

# Aplicar toda la infraestructura (desde la raíz del repo)
./src/infrastructure/terraform/scripts/apply.sh

# Destruir toda la infraestructura
./src/infrastructure/terraform/scripts/destroy.sh
```

Los scripts aplican/destruyen los stacks en el orden correcto de dependencia (primero red, luego RDS, luego ECS, etc.).

## Costos estimados

| Componente | Tipo | Costo aprox. (MVP) |
|---|---|---|
| ECS Fargate | 6 servicios, tamaño mínimo | ~$20-40/mes |
| RDS Aurora | db.t3.micro | ~$30/mes |
| ALB | 1 load balancer | ~$20/mes |
| CloudFront + S3 | Tráfico bajo | ~$5/mes |
| ECR | 6 repositorios | ~$1/mes |
