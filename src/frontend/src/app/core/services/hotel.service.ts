import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';
import { environment } from '../../../environments/environment';

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
  amenidades: string[];
  imagenes: string[];
  precio_minimo: number;
  created_at: string;
}

export interface ListaHotelesResponse {
  total: number;
  hoteles: HotelListItem[];
}

export interface HotelListParams {
  limit?: number;
  offset?: number;
  ciudad?: string;
  precio_min?: number;
  precio_max?: number;
  estrellas?: number[];
  amenidades_populares?: string[];
  capacidad_min?: number;
  orden?: 'precio_asc' | 'precio_desc' | 'rating_desc' | 'nombre_asc' | 'nombre_desc';
}

@Injectable({ providedIn: 'root' })
export class HotelService {
  private readonly api = inject(ApiService);
  private readonly http = inject(HttpClient);
  private readonly baseUrl = environment.apiUrl;

  listHotels(params: HotelListParams = {}): Observable<ListaHotelesResponse> {
    let httpParams = new HttpParams()
      .set('limit', String(params.limit ?? 10))
      .set('offset', String(params.offset ?? 0));

    if (params.orden) httpParams = httpParams.set('orden', params.orden);
    if (params.ciudad) httpParams = httpParams.set('ciudad', params.ciudad);
    if (params.capacidad_min != null) httpParams = httpParams.set('capacidad_min', String(params.capacidad_min));
    if (params.precio_min != null) httpParams = httpParams.set('precio_min', String(params.precio_min));
    if (params.precio_max != null) httpParams = httpParams.set('precio_max', String(params.precio_max));
    params.estrellas?.forEach(e => { httpParams = httpParams.append('estrellas', String(e)); });
    params.amenidades_populares?.forEach(a => { httpParams = httpParams.append('amenidades_populares', a); });

    return this.http.get<ListaHotelesResponse>(`${this.baseUrl}/hoteles`, { params: httpParams });
  }

  getHotelById(id: string): Observable<HotelDetalle> {
    return this.api.get<HotelDetalle>(`/hoteles/${id}`);
  }

  listCountries(): Observable<{ paises: string[] }> {
    return this.api.get<{ paises: string[] }>('/hoteles/paises');
  }
}
