import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';

export interface BookingResponse {
  id: string;
  usuario_id: string;
  habitacion_id: string;
  fecha_entrada: string;
  fecha_salida: string;
  num_huespedes: number;
  estado: string;
  pago_id: string | null;
  created_at: string;
}

export interface BookingListResponse {
  total: number;
  reservas: BookingResponse[];
}

@Injectable({ providedIn: 'root' })
export class BookingService {
  private readonly api = inject(ApiService);

  getUserBookings(userId: string, params?: { skip?: number; limit?: number }): Observable<BookingListResponse> {
    const limit = params?.limit ?? 10;
    const skip = params?.skip ?? 0;
    return this.api.get<BookingListResponse>(`/reservas/usuario/${userId}`, { skip, limit });
  }
}
