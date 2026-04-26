import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';

export type BookingStatus = 'pendiente' | 'confirmada' | 'cancelada' | 'completada';
export type BookingFilter = 'activas' | 'canceladas' | 'pasadas';

export interface BookingResponse {
  id: string;
  habitacion_id: string;
  nombre_habitacion: string | null;
  nombre_hotel: string | null;
  imagenes_hotel: string[];
  ciudad_hotel?: string | null;
  pais_hotel?: string | null;
  fecha_entrada: string;
  fecha_salida: string;
  num_huespedes: number;
  estado: BookingStatus;
  pago_id?: string | null;
  created_at?: string;
}

export interface BookingListResponse {
  total: number;
  reservas: BookingResponse[];
}

export interface CreateBookingRequest {
  habitacion_id: string;
  fecha_entrada: string;
  fecha_salida: string;
  num_huespedes: number;
  pago_id: string | null;
}

@Injectable({ providedIn: 'root' })
export class BookingService {
  private readonly api = inject(ApiService);

  createReservation(body: CreateBookingRequest): Observable<BookingResponse> {
    return this.api.post<BookingResponse>('/reservas', body);
  }

  getUserBookings(userId: string, params?: { skip?: number; limit?: number }): Observable<BookingListResponse> {
    const limit = params?.limit ?? 10;
    const skip = params?.skip ?? 0;
    return this.api.get<BookingListResponse>(`/reservas/usuario/${userId}`, { skip, limit });
  }

  getBookingsByStatus(status: BookingFilter): Observable<BookingListResponse> {
    return this.api.get<BookingListResponse>('/reservas', { estado: status });
  }
}
