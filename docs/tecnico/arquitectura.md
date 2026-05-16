# Arquitectura General — TravelHub

## Diagrama de componentes

```mermaid
graph TB
    subgraph Clientes
        WEB([Usuario Web\nAngular 19])
        APP([App iOS\nSwiftUI])
    end

    subgraph AWS
        subgraph Frontend
            CF[CloudFront CDN]
            S3[S3 — archivos estáticos Angular]
        end

        subgraph LoadBalancing
            ALB[Application Load Balancer\npath-based routing]
        end

        subgraph Compute [ECS Fargate]
            SVC_USR[usuarios :8002]
            SVC_BSQ[busquedas :8003]
            SVC_HOT[hoteles :8004]
            SVC_RES[reservas :8006]
            SVC_NOT[notificaciones :8007]
            SVC_PAG[pagos :8008]
        end

        subgraph Storage
            RDS[(RDS PostgreSQL 15\ndb.t3.micro)]
            REDIS[(ElastiCache Redis)]
            SQS[SQS Queue\ntravelhub-queue]
            SM[Secrets Manager\nJWT · RSA · DB URL]
        end
    end

    WEB -->|HTTPS| CF
    CF --> S3
    WEB -->|API calls /api/*| ALB
    APP -->|HTTPS /api/*| ALB
    ALB -->|/api/usuarios/*| SVC_USR
    ALB -->|/api/busquedas/*| SVC_BSQ
    ALB -->|/api/hoteles/*| SVC_HOT
    ALB -->|/api/reservas/*| SVC_RES
    ALB -->|/api/notificaciones/*| SVC_NOT
    ALB -->|/api/pagos/*| SVC_PAG
    SVC_USR & SVC_BSQ & SVC_HOT & SVC_RES & SVC_NOT & SVC_PAG --> RDS
    SVC_BSQ --> REDIS
    SVC_RES --> SQS
    SQS --> SVC_NOT
```

## Decisiones de arquitectura

### Microservicios independientes

Cada servicio tiene su propia base de datos lógica (mismo servidor RDS, distinto schema/tablas) y se despliega de forma independiente. Esto permite escalar y desplegar `busquedas` sin tocar `pagos`.

### Routing por path en el ALB

El ALB distingue servicios por prefijo de ruta:

| Ruta | Servicio |
|---|---|
| `/api/usuarios/*` | usuarios |
| `/api/busquedas/*` | busquedas |
| `/api/hoteles/*` | hoteles |
| `/api/reservas/*` | reservas |
| `/api/notificaciones/*` | notificaciones |
| `/api/pagos/*` | pagos |

En desarrollo local, nginx en el puerto `8080` replica este comportamiento.

### Comunicación entre servicios

Aunque el diseño busca desacoplamiento, actualmente sí existen llamadas síncronas entre microservicios:

- `reservas` consulta a `hoteles` vía HTTP (`/hoteles/habitaciones` y `/hoteles/habitaciones/resumen`) para validar y enriquecer la información de habitaciones.

Adicionalmente, la arquitectura contempla comunicación asíncrona vía SQS para eventos de reservas y notificaciones.

### Caché

`busquedas` usa Redis para cachear resultados de búsqueda frecuentes y reducir carga sobre RDS.

## Puertos en desarrollo local

| Servicio | Puerto | Swagger UI |
|---|---|---|
| nginx (gateway) | 8080 | http://localhost:8080/docs |
| usuarios | 8002 | http://localhost:8002/docs |
| busquedas | 8003 | http://localhost:8003/docs |
| hoteles | 8004 | http://localhost:8004/docs |
| reservas | 8006 | http://localhost:8006/docs |
| notificaciones | 8007 | http://localhost:8007/docs |
| pagos | 8008 | http://localhost:8008/docs |

## Stack tecnológico

| Capa | Tecnología | Versión |
|---|---|---|
| Web | Angular | 19 |
| Móvil | SwiftUI | iOS 17+ |
| Backend | FastAPI + Python | 3.12 |
| Base de datos | PostgreSQL | 15 |
| Caché | Redis | 7 |
| Mensajería | AWS SQS | — |
| Cloud | AWS (ECS Fargate, ALB, RDS Aurora, CloudFront) | — |
| IaC | Terraform | — |
| CI/CD | GitHub Actions + AWS CodePipeline/CodeBuild/CodeDeploy | — |
| Contenedores | Docker | — |
