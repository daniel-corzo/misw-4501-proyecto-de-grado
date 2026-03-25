# TravelHub Backend

This is the backend for the TravelHub application, built using FastAPI microservices.

## Authentication and RBAC
This project uses **JWT (RS256)** for authentication and decentralizing validation for microservices.
- `auth`: Manages `UserCredentials` (email, hashed password, role) and issues JWTs signed with `JWT_PRIVATE_KEY`.
- `usuarios`: Manages `UserProfile` (first name, last name, telephone).
- Other microservices validate JWTs using `JWT_PUBLIC_KEY` locally using the `travelhub_common` library.

### Generate RSA Keys (Local Development)
To run these services locally, you will need to generate a self-signed RSA key pair.
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

### Making Authenticated Requests
To make requests to protected services, register a user and complete a login on the `auth` service.
Include the generated `access_token` in your headers:
```
Authorization: Bearer <your_access_token_here>
```

### Registration & Cross-Service Flow
Registration acts as a unified mechanism spanning seamlessly over `usuarios` and `auth`.
When a client hits `POST /usuarios`:
1. The `usuarios` microservice securely generates the initial state UUID ensuring data normalization rules.
2. It orchestrates an internal HTTP call, mirroring credentials securely to the `auth` microservice encapsulating the same ID matching.
3. Because the remote MS is called asynchronously inline, the `usuarios` endpoint safely triggers a parent `db.rollback()` gracefully cascading errors via HTTP if validation or network availability fails inside `auth`!
