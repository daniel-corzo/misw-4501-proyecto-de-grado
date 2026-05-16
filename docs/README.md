# TravelHub — Documentación

Documentación oficial del proyecto TravelHub, plataforma de reservas hoteleras para Latinoamérica desarrollada como proyecto de grado en la Universidad de Los Andes (MISW 4501/4502).

## Contenido

### Documentación técnica

Para desarrolladores, integradores y revisores técnicos.

| Documento | Descripción |
|---|---|
| [Arquitectura general](tecnico/arquitectura.md) | Diagrama de componentes, flujos de red y decisiones de diseño |
| [Backend — microservicios](tecnico/backend/README.md) | Índice de los 6 microservicios FastAPI |
| [Frontend Angular](tecnico/frontend.md) | Estructura de módulos, rutas, guards e interceptores |
| [App móvil iOS](tecnico/mobile.md) | Arquitectura SwiftUI, capas y navegación |
| [Infraestructura AWS](tecnico/infraestructura.md) | Terraform, ECS Fargate, CI/CD pipelines |
| [Seguridad](tecnico/seguridad.md) | JWT, RSA-OAEP en pagos, Secrets Manager |
| [Desarrollo local](tecnico/desarrollo-local.md) | Setup completo para correr el proyecto en tu máquina |

### Guía de usuario

Para usuarios finales (viajeros y socios hoteleros).

| Documento | Descripción |
|---|---|
| [Primeros pasos](usuario/primeros-pasos.md) | Crear cuenta e iniciar sesión |
| [Buscar alojamiento](usuario/buscar-alojamiento.md) | Buscar hoteles y ver disponibilidad |
| [Hacer una reserva](usuario/hacer-reserva.md) | Seleccionar habitación, pagar y confirmar |
| [Gestionar reservas](usuario/gestionar-reservas.md) | Ver historial, detalle y cancelar |
| [App móvil iOS](usuario/app-movil.md) | Uso de la aplicación en iPhone |

## Sobre el proyecto

TravelHub conecta viajeros con propiedades hoteleras en diferentes países. Permite buscar alojamiento, reservar, pagar y gestionar reservas desde web o móvil.

**Stack:** Angular 19 · SwiftUI (iOS) · FastAPI (Python 3.12) · PostgreSQL · Redis · AWS (ECS Fargate, ALB, SQS, RDS Aurora)
