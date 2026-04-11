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
