import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';
import type { HabitacionDetalle } from './hotel.service';

export type BookingStatus = 'pendiente' | 'confirmada' | 'cancelada' | 'completada';
export type BookingFilter = 'activas' | 'canceladas' | 'pasadas';
export type PaymentStatus = 'successful' | 'failed';
export type PaymentStatusFilter = PaymentStatus | 'pending';

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

export interface HotelBookingResponse extends BookingResponse {
  nombre_viajero: string | null;
  email_viajero: string | null;
  numero_habitacion: string | null;
  total_noches: number;
  monto_total: number | null;
  estado_pago: PaymentStatus | null;
}

export interface HotelBookingListResponse {
  total: number;
  reservas: HotelBookingResponse[];
  habitaciones: HabitacionDetalle[];
}

export interface BookingDetailHotel {
  id: string | null;
  nombre: string;
  direccion: string | null;
  ciudad: string | null;
  pais: string | null;
  estrellas: number | null;
  ranking: number | null;
  imagenes: string[];
  contacto_celular: string | null;
  contacto_email: string | null;
  check_in: string | null;
  check_out: string | null;
}

export interface BookingDetailRoom {
  id: string;
  nombre: string;
  descripcion: string | null;
  numero: string | null;
  capacidad: number | null;
  imagenes: string[];
  monto: number | null;
  impuestos: number | null;
}

export interface BookingDetailResponse {
  id: string;
  codigo_reserva: string;
  estado: BookingStatus;
  fecha_entrada: string;
  fecha_salida: string;
  num_huespedes: number;
  pago_id: string | null;
  created_at: string;
  hotel: BookingDetailHotel;
  habitacion: BookingDetailRoom;
  amenidades_hotel: string[];
}

export interface HotelBookingTravelerDetail {
  id: string;
  nombre: string | null;
  email: string | null;
}

export interface HotelBookingPaymentDetail {
  id: string | null;
  estado: PaymentStatusFilter;
  monto: number | null;
  medio_de_pago: string | null;
  created_at: string | null;
  tarjeta_ultimos_4: string | null;
}

export interface HotelBookingDetailResponse extends BookingDetailResponse {
  viajero: HotelBookingTravelerDetail;
  pago: HotelBookingPaymentDetail;
  total_noches: number;
  monto_total: number | null;
  qr_checkin_payload: string;
}

export interface CreateBookingRequest {
  habitacion_id: string;
  fecha_entrada: string;
  fecha_salida: string;
  num_huespedes: number;
  pago_id: string | null;
}

/** PATCH /reservas/{id} — at least one field required by backend. */
export interface UpdateBookingRequest {
  fecha_entrada?: string;
  fecha_salida?: string;
  num_huespedes?: number;
  habitacion_id?: string;
}

export interface HotelReservationsFilters {
  nombre_viajero?: string;
  tipo_habitacion?: string;
  estado?: BookingStatus;
  fecha_inicio?: string;
  fecha_fin?: string;
  estado_pago?: PaymentStatusFilter;
  num_huespedes?: number;
}

@Injectable({ providedIn: 'root' })
export class BookingService {
  private readonly api = inject(ApiService);

  createReservation(body: CreateBookingRequest): Observable<BookingResponse> {
    return this.api.post<BookingResponse>('/reservas', body);
  }

  updateReservation(
    reservaId: string,
    body: UpdateBookingRequest
  ): Observable<BookingResponse> {
    return this.api.patch<BookingResponse>(`/reservas/${reservaId}`, body);
  }

  getUserBookings(userId: string, params?: { skip?: number; limit?: number }): Observable<BookingListResponse> {
    const limit = params?.limit ?? 10;
    const skip = params?.skip ?? 0;
    return this.api.get<BookingListResponse>(`/reservas/usuario/${userId}`, { skip, limit });
  }

  getBookingsByStatus(status: BookingFilter): Observable<BookingListResponse> {
    return this.api.get<BookingListResponse>('/reservas', { estado: status });
  }

  getHotelReservations(skip = 0, limit = 10, filters?: HotelReservationsFilters): Observable<HotelBookingListResponse> {
    const params: Record<string, string | number> = { skip, limit };
    if (filters) {
      if (filters.nombre_viajero) params['nombre_viajero'] = filters.nombre_viajero;
      if (filters.tipo_habitacion) params['tipo_habitacion'] = filters.tipo_habitacion;
      if (filters.estado) params['estado'] = filters.estado;
      if (filters.fecha_inicio) params['fecha_inicio'] = filters.fecha_inicio;
      if (filters.fecha_fin) params['fecha_fin'] = filters.fecha_fin;
      if (filters.estado_pago) params['estado_pago'] = filters.estado_pago;
      if (filters.num_huespedes !== undefined) params['num_huespedes'] = filters.num_huespedes;
    }
    return this.api.get<HotelBookingListResponse>('/reservas/hoteles', params);
  }

  getBookingById(bookingId: string): Observable<BookingDetailResponse> {
    return this.api.get<BookingDetailResponse>(`/reservas/${bookingId}`);
  }

  getHotelBookingById(bookingId: string): Observable<HotelBookingDetailResponse> {
    return this.api.get<HotelBookingDetailResponse>(`/reservas/hoteles/${bookingId}`);
  }

  cancelReservation(bookingId: string): Observable<BookingResponse> {
    return this.api.patch<BookingResponse>(`/reservas/${bookingId}/cancelar`, {});
  }

  confirmHotelReservation(bookingId: string): Observable<HotelBookingResponse> {
    return this.api.patch<HotelBookingResponse>(`/reservas/${bookingId}/confirmar`, {});
  }

  rejectHotelReservation(bookingId: string): Observable<HotelBookingResponse> {
    return this.api.patch<HotelBookingResponse>(`/reservas/${bookingId}/rechazar`, {});
  }
}
