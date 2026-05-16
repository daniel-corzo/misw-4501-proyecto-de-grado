# Backend de TravelHub

Este es el backend de la aplicación TravelHub, construido con microservicios FastAPI.

## Acceso y RBAC

Este proyecto usa **JWT (RS256)** para la autenticación y la validación descentralizada entre microservicios.

- **`usuarios`**: registra usuarios (`POST /usuarios`), guarda credenciales y perfiles, emite JWT firmados con `JWT_PRIVATE_KEY` y expone los endpoints de sesión en el mismo servicio.
- **Los demás microservicios** validan JWT con `JWT_PUBLIC_KEY` mediante la librería `travelhub_common` y verifican la revocación contra la tabla `revoked_tokens` en su `DB_URL` configurado, cuando aplica.

### Generar claves RSA (desarrollo local)

Para ejecutar estos servicios localmente, necesitas un par de claves RSA autofirmadas.

```bash
# Generar clave privada
openssl genrsa -out private.pem 2048

# Generar clave pública
openssl rsa -in private.pem -outform PEM -pubout -out public.pem
```

Luego configura tus variables `.env` serializadas como texto:

```env
JWT_PRIVATE_KEY="-----BEGIN RSA PRIVATE KEY-----\nMIIE...\n-----END RSA PRIVATE KEY-----"
JWT_PUBLIC_KEY="-----BEGIN PUBLIC KEY-----\nMIIB...\n-----END PUBLIC KEY-----"
```

### Hacer solicitudes autenticadas a la API

Regístrate con `POST /usuarios` y luego obtén un `access_token` mediante el endpoint de inicio de sesión del servicio **usuarios** (o a través del prefijo del API gateway que use tu despliegue).

Incluye el token en las solicitudes a rutas protegidas:

```
Authorization: Bearer <your_access_token_here>
```

### Registro

El registro es un solo paso: `POST /usuarios` crea el registro del usuario (credenciales, rol y campos de perfil como los datos del viajero) en una sola transacción.

## Correos de reserva

TravelHub envía correos para el viajero desde el backend cuando una reserva se confirma, se cancela o se paga con éxito.

### Configuración SMTP

Configura los ajustes compartidos del backend con las credenciales SMTP de Amazon SES generadas para tu usuario SMTP de SES:

```env
SMTP_HOST=email-smtp.us-east-1.amazonaws.com
SMTP_PORT=587
SMTP_USER=<amazon_ses_smtp_username>
SMTP_PASS=<amazon_ses_smtp_password>
SMTP_FROM_EMAIL=<verified_sender_email>
SMTP_SENDER_NAME=TravelHub
SMTP_USE_TLS=true
SMTP_TIMEOUT_SECONDS=30
FRONTEND_BASE_URL=https://travel-hub.online
```

Notas:

- Los correos se envían como un efecto secundario de mejor esfuerzo después de que la reserva o el pago ya se hayan confirmado.
- Si falla la entrega SMTP, ni la confirmación/cancelación de la reserva ni el pago se revierten.
- Los correos de recibo de pago se activan cuando `POST /pagos/pagar` recibe un `reserva_id` que puede usarse para obtener los detalles de la reserva mostrados en el correo.

### Contenido del correo

Los correos de reserva se generan solo en español e incluyen:

- Marca de TravelHub y un enlace a `https://travel-hub.online`
- Un ícono visual grande de estado para confirmación, cancelación o recibo de pago
- Detalles de la reserva como ID, hotel, habitación, fechas y número de huéspedes
- Detalles del pago en el correo de recibo cuando el pago es exitoso

### Internacionalización futura

La internacionalización se pospone intencionalmente para esta funcionalidad. Cuando se agregue localización más adelante, se recomienda este enfoque:

1. Mover todas las cadenas visibles del asunto y del cuerpo a diccionarios o plantillas específicas por idioma, organizadas por tipo de notificación.
2. Mantener el armado de los datos de reserva y pago independiente del idioma para que el mismo modelo de datos pueda alimentar varios idiomas.
3. Seleccionar el idioma desde el perfil del viajero o el contexto de la solicitud y renderizar el asunto y el cuerpo finales desde ese conjunto de plantillas específico.
