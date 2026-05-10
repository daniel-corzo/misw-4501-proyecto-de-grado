export const environment = {
  production: false,
  apiUrl: 'http://localhost:8080/api',
  // RSA-OAEP public key PEM used to encrypt card payloads before sending to /pagos/pagar.
  // Must match the PAGO_RSA_PRIVATE_KEY_PEM secret configured in the pagos backend service.
  // Generate a key pair with utils/generate_keys.py and paste the public key here.
  rsaPublicKeyPem:
    '-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAt9qtnYollQSoCoZ54KMC\nG6CWjN7+m08+uoJTusrAOOHF5qUML1TxCmyoxxZolN8Vmk86YBaK0idS0d7Z0Yt3\nWGwC9jKPs3mfEsTZT0kVobehz4XsQoH+zo9ZrKEiAOK+Cp4bUKk9pAH6Dzqgo9Xc\nCC9wzTzzWnAMCTaaQ/l10oE0Gaqp/D+dqGmmgxEoReHgAM2soYTvSjG2ijlhY+Vk\n/RpSdvl9miSoCanzJpB6BPHn7PzC9Suo/zP+2TTOT2usSkGn46FMkY3W3wDLjnb5\nU8jDktZkYYKsxwpm0nV/Mj25mDyGxgm9uiOygnruXypKC7nJGZT810F3/VlhXzG9\n2wIDAQAB\n-----END PUBLIC KEY-----\n',
};
