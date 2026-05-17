# Documentación técnica — TravelHub

Referencia para desarrolladores del proyecto.

## Archivos

| Archivo | Contenido |
|---|---|
| [arquitectura.md](arquitectura.md) | Diagrama general del sistema, servicios AWS, routing del ALB y comunicación entre microservicios |
| [seguridad.md](seguridad.md) | Autenticación JWT RS256, cifrado RSA-OAEP de pagos y gestión de secretos en AWS Secrets Manager |
| [infraestructura.md](infraestructura.md) | Componentes AWS (ECS Fargate, RDS, ElastiCache, CloudFront), pipelines CI/CD y Terraform |
| [desarrollo-local.md](desarrollo-local.md) | Cómo levantar el proyecto localmente: requisitos, variables de entorno y comandos útiles |
| [frontend.md](frontend.md) | Stack Angular 19, estructura del proyecto, rutas, guards e interceptores |
| [accesibilidad-i18n.md](accesibilidad-i18n.md) | Internacionalización con Transloco (es/en) y modos de accesibilidad (daltonismo, tamaño de fuente) |
| [mobile.md](mobile.md) | App iOS en SwiftUI, arquitectura MVVM, flujos principales y configuración de builds |
| [backend/](backend/README.md) | Documentación de cada microservicio (usuarios, búsquedas, hoteles, reservas, pagos, notificaciones) |
