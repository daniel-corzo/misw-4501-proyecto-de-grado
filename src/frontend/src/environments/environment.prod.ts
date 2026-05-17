export const environment = {
  production: true,
  apiUrl: 'https://da8n5gsw578s6.cloudfront.net/api',
  // RSA-OAEP public key PEM used to encrypt card payloads before sending to /pagos/pagar.
  // Must match the PAGO_RSA_PRIVATE_KEY_PEM secret configured in the pagos backend service.
  rsaPublicKeyPem: '',
};
