import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
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
    return this.api.post<PayResponse>('/pagos/pagar', {
      monto: req.monto,
      medio_de_pago: 'credit_card',
      debe_fallar: false,
      numero: this.normalizePAN(req.cardNumber),
      cvv: req.cvv.trim(),
      fecha_expiracion: this.normalizeExpiry(req.expirationDate),
    });
  }

  private normalizePAN(raw: string): string {
    return raw.replace(/\D/g, '');
  }

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
}
