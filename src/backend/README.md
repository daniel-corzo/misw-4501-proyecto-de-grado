# TravelHub Backend

This is the backend for the TravelHub application, built using FastAPI microservices.

## Access and RBAC

This project uses **JWT (RS256)** for authentication and decentralized validation across microservices.

- **`usuarios`**: Registers users (`POST /usuarios`), stores credentials and profiles, issues JWTs signed with `JWT_PRIVATE_KEY`, and exposes session endpoints on the same service.
- **Other microservices** validate JWTs using `JWT_PUBLIC_KEY` via the `travelhub_common` library and check revocation against the `revoked_tokens` table on their configured `DB_URL` where applicable.

### Generate RSA Keys (Local Development)

To run these services locally, you will need a self-signed RSA key pair.

```bash
# Generate private key
openssl genrsa -out private.pem 2048

# Generate public key
openssl rsa -in private.pem -outform PEM -pubout -out public.pem
```

Then configure your `.env` variables stringified:

```env
JWT_PRIVATE_KEY="-----BEGIN RSA PRIVATE KEY-----\nMIIE...\n-----END RSA PRIVATE KEY-----"
JWT_PUBLIC_KEY="-----BEGIN PUBLIC KEY-----\nMIIB...\n-----END PUBLIC KEY-----"
```

### Making Authenticated API Requests

Register with `POST /usuarios`, then obtain an `access_token` via the login endpoint on the **usuarios** service (or through the API gateway prefix your deployment uses).

Include the token in requests to protected routes:

```
Authorization: Bearer <your_access_token_here>
```

### Registration

Sign-up is a single step: `POST /usuarios` creates the user record (credentials, role, profile fields such as traveler data) in one transaction.

## Booking Emails

TravelHub sends traveler-facing emails from the backend when a reservation is confirmed, cancelled, or paid successfully.

### SMTP Configuration

Configure the shared backend settings with the Amazon SES SMTP credentials generated for your SES SMTP user:

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

Notes:

- Emails are sent as a best-effort side effect after the reservation or payment has already been committed.
- If SMTP delivery fails, the reservation confirmation/cancellation or the payment itself is not rolled back.
- Payment receipt emails are triggered when `POST /pagos/pagar` receives a `reserva_id` that can be used to fetch the reservation details shown in the email.

### Email Content

The booking emails are generated in Spanish only and include:

- TravelHub branding and a link to `https://travel-hub.online`
- A large visual status icon for confirmation, cancellation, or payment receipt
- Reservation details such as ID, hotel, room, dates, and number of guests
- Payment details in the receipt email when the payment is successful

### Future Internationalization

Internationalization is intentionally deferred for this feature. When localization is added later, prefer this approach:

1. Move all visible subject/body strings into locale-specific dictionaries or templates keyed by notification type.
2. Keep reservation and payment payload assembly language-neutral so the same data model can feed multiple locales.
3. Select the locale from the traveler profile or request context and render the final subject/body from that locale-specific template set.
