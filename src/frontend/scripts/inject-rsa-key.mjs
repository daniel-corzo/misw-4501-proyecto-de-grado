/**
 * inject-rsa-key.mjs
 *
 * Reads PAGO_RSA_PUBLIC_KEY_PEM from the environment and writes it into
 * environment.prod.ts before the Angular production build runs.
 *
 * Usage (automatic via `prebuild`):
 *   PAGO_RSA_PUBLIC_KEY_PEM="$(cat payment_public.pem)" npm run build
 *
 * Fails the build (exit 1) when the variable is missing or empty.
 */

import { readFileSync, writeFileSync } from 'fs';
import { fileURLToPath } from 'url';
import { join, dirname } from 'path';

const __dir = dirname(fileURLToPath(import.meta.url));
const envProdPath = join(__dir, '..', 'src', 'environments', 'environment.prod.ts');

const pem = process.env['PAGO_RSA_PUBLIC_KEY_PEM'];

if (!pem || !pem.trim()) {
  console.error(
    '\n[inject-rsa-key] ERROR: PAGO_RSA_PUBLIC_KEY_PEM environment variable is not set.\n' +
    'Set it to the RSA public key PEM matching the pagos service PAGO_RSA_PRIVATE_KEY_PEM.\n' +
    'Example:\n' +
    '  export PAGO_RSA_PUBLIC_KEY_PEM="$(cat payment_public.pem)"\n' +
    '  npm run build\n'
  );
  process.exit(1);
}

if (!pem.includes('BEGIN PUBLIC KEY')) {
  console.error(
    '\n[inject-rsa-key] ERROR: PAGO_RSA_PUBLIC_KEY_PEM does not look like a valid PEM public key.\n' +
    'Expected a string containing "-----BEGIN PUBLIC KEY-----".\n'
  );
  process.exit(1);
}

const existing = readFileSync(envProdPath, 'utf-8');

// Replace the rsaPublicKeyPem value (empty or previously injected) with the new key.
// Uses a regex so it works regardless of whether the current value is empty or already set.
const escaped = pem.replace(/`/g, '\\`').replace(/\$/g, '\\$');
const updated = existing.replace(
  /rsaPublicKeyPem:\s*`[^`]*`|rsaPublicKeyPem:\s*'[^']*'/,
  `rsaPublicKeyPem: \`${escaped}\``
);

if (updated === existing) {
  console.error(
    '\n[inject-rsa-key] ERROR: Could not find rsaPublicKeyPem in environment.prod.ts.\n' +
    'Make sure the file contains: rsaPublicKeyPem: \'\'\n'
  );
  process.exit(1);
}

writeFileSync(envProdPath, updated, 'utf-8');
console.log('[inject-rsa-key] RSA public key injected into environment.prod.ts ✓');
