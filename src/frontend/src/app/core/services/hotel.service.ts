import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';

export interface HabitacionDetalle {
  id: string;
  capacidad: number;
  numero: string;
  descripcion: string | null;
  imagenes: string[];
  monto: number;
  impuestos: number;
  disponible: boolean;
}

export interface PoliticaDetalle {
  id: string;
  nombre: string;
  descripcion: string | null;
  tipo: string;
  penalizacion: number;
  dias_antelacion: number;
}

export interface HotelDetalle {
  id: string;
  nombre: string;
  direccion: string;
  ciudad: string;
  estado: string | null;
  departamento: string;
  pais: string;
  descripcion: string | null;
  amenidades: string[];
  estrellas: number;
  ranking: number;
  contacto_celular: string | null;
  contacto_email: string | null;
  imagenes: string[];
  check_in: string;
  check_out: string;
  valor_minimo_modificacion: number;
  usuario_id: string;
  created_at: string;
  updated_at: string;
  politicas: PoliticaDetalle[];
  habitaciones: HabitacionDetalle[];
}

export interface HotelListItem {
  id: string;
  nombre: string;
  ciudad: string;
  pais: string;
  estrellas: number;
  imagenes: string[];
  precio_minimo: number;
  created_at: string;
}

export interface ListaHotelesResponse {
  total: number;
  hoteles: HotelListItem[];
}

@Injectable({ providedIn: 'root' })
export class HotelService {
  private readonly api = inject(ApiService);

  listHotels(params?: { limit?: number; offset?: number }): Observable<ListaHotelesResponse> {
    const limit = params?.limit ?? 20;
    const offset = params?.offset ?? 0;
    return this.api.get<ListaHotelesResponse>('/hoteles', { limit, offset });
  }

  getHotelById(id: string): Observable<HotelDetalle> {
    return this.api.get<HotelDetalle>(`/hoteles/${id}`);
  }
}
