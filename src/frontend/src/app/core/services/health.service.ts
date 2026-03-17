import { Injectable, inject } from '@angular/core';
import { Observable, forkJoin, of } from 'rxjs';
import { catchError, map } from 'rxjs/operators';
import { ApiService } from './api.service';

export interface ServiceHealth {
  name: string;
  status: 'healthy' | 'unhealthy' | 'loading';
  responseTime: number | null;
}

const SERVICES: string[] = [
  'autenticacion',
  'usuarios',
  'busqueda',
  'hoteles',
  'inventario',
  'reservas',
  'pagos',
  'notificaciones',
];

@Injectable({ providedIn: 'root' })
export class HealthService {
  private readonly api = inject(ApiService);

  /**
   * Llama a GET /api/{servicio}/health por cada microservicio a través del gateway.
   * El gateway hace pass-through y cada servicio responde con su /health del common.
   */
  checkAll(): Observable<ServiceHealth[]> {
    const checks$ = SERVICES.map((name) => {
      const start = Date.now();
      return this.api.get<{ status: string }>(`/${name}/health`).pipe(
        map((res) => ({
          name,
          status: res.status === 'healthy' ? ('healthy' as const) : ('unhealthy' as const),
          responseTime: Date.now() - start,
        })),
        catchError(() =>
          of<ServiceHealth>({ name, status: 'unhealthy', responseTime: null })
        )
      );
    });

    return forkJoin(checks$);
  }
}
