import { Injectable, inject } from '@angular/core';
import { Observable, from } from 'rxjs';
import { environment } from '../../../environments/environment';
import { ApiService } from './api.service';

export interface PayRequest {
  cardholderName: string;
  cardNumber: string;
  cvv: string;
  expirationDate: string;
  monto: number;
}

export interface PayResponse {
  id: string;
  monto: number;
  medio_de_pago: string;
  estado: string;
  tarjeta_ultimos_4: string | null;
  created_at: string;
  updated_at: string;
}

@Injectable({ providedIn: 'root' })
export class PaymentService {
  private readonly api = inject(ApiService);

  pay(req: PayRequest): Observable<PayResponse> {
    return from(this.payAsync(req));
  }

  private async payAsync(req: PayRequest): Promise<PayResponse> {
    const payloadCifrado = await this.encryptCardPayload(
      this.normalizePAN(req.cardNumber),
      req.cvv.trim(),
      this.normalizeExpiry(req.expirationDate)
    );

    return await new Promise<PayResponse>((resolve, reject) => {
      this.api
        .post<PayResponse>('/pagos/pagar', {
          monto: req.monto,
          medio_de_pago: 'credit_card',
          debe_fallar: false,
          payload_cifrado: payloadCifrado,
        })
        .subscribe({ next: resolve, error: reject });
    });
  }

  /** Strip all non-digit characters from the PAN. */
  private normalizePAN(raw: string): string {
    return raw.replace(/\D/g, '');
  }

  /**
   * Accepts MM/YY → MM/20YY.
   * Accepts MM/YYYY → unchanged.
   * Otherwise returns trimmed input.
   */
  private normalizeExpiry(raw: string): string {
    const trimmed = raw.trim();
    const parts = trimmed.split('/');
    if (parts.length !== 2) return trimmed;
    const [mm, yyOrYyyy] = parts;
    if (mm.length !== 2 || !/^\d+$/.test(mm)) return trimmed;
    if (yyOrYyyy.length === 4 && /^\d+$/.test(yyOrYyyy)) return trimmed;
    if (yyOrYyyy.length === 2 && /^\d+$/.test(yyOrYyyy)) return `${mm}/20${yyOrYyyy}`;
    return trimmed;
  }

  private async encryptCardPayload(
    numero: string,
    cvv: string,
    fechaExpiracion: string
  ): Promise<string> {
    if (!environment.rsaPublicKeyPem) {
      throw new Error(
        '[PaymentService] rsaPublicKeyPem is not configured in environment. ' +
        'Generate a key pair with utils/generate_keys.py and set the public key in environment.ts.'
      );
    }
    const publicKey = await this.importPublicKey(environment.rsaPublicKeyPem);
    const plaintext = JSON.stringify({ numero, cvv, fecha_expiracion: fechaExpiracion });
    console.debug('[PaymentService] Plaintext to encrypt:', plaintext);

    const encoded = new TextEncoder().encode(plaintext);
    const ciphertext = await window.crypto.subtle.encrypt(
      { name: 'RSA-OAEP' },
      publicKey,
      encoded
    );

    // Avoid spread operator for large buffers
    const bytes = new Uint8Array(ciphertext);
    let binary = '';
    for (let i = 0; i < bytes.length; i++) {
      binary += String.fromCharCode(bytes[i]);
    }
    const b64 = btoa(binary);
    console.debug('[PaymentService] payload_cifrado length:', b64.length);
    return b64;
  }

  private async importPublicKey(pem: string): Promise<CryptoKey> {
    const lines = pem
      .split('\n')
      .map((l) => l.trim())
      .filter((l) => l.length > 0);

    const beginIdx = lines.findIndex((l) => l.includes('BEGIN'));
    const endIdx = lines.findIndex((l) => l.includes('END'));

    if (beginIdx === -1 || endIdx === -1 || endIdx <= beginIdx) {
      throw new Error('Invalid RSA public key PEM');
    }

    const b64Body = lines.slice(beginIdx + 1, endIdx).join('');
    console.debug('[PaymentService] PEM body length:', b64Body.length);

    // Decode base64 → binary string → Uint8Array (avoid spread for large buffers)
    const binaryStr = atob(b64Body);
    const der = new Uint8Array(binaryStr.length);
    for (let i = 0; i < binaryStr.length; i++) {
      der[i] = binaryStr.charCodeAt(i);
    }

    return window.crypto.subtle.importKey(
      'spki',
      der,
      { name: 'RSA-OAEP', hash: { name: 'SHA-256' } },
      false,
      ['encrypt']
    );
  }
}
