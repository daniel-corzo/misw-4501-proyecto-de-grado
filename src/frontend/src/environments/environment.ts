export const environment = {
  production: false,
  apiUrl: 'http://localhost:8080/api',
  // RSA-OAEP public key PEM used to encrypt card payloads before sending to /pagos/pagar.
  // Must match the PAGO_RSA_PRIVATE_KEY_PEM secret configured in the pagos backend service.
  // Generate a key pair with utils/generate_keys.py and paste the public key here.
  rsaPublicKeyPem: '',
};
