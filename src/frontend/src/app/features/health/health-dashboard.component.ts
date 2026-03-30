import { Component, inject, signal, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HealthService, ServiceHealth } from '../../core/services/health.service';

@Component({
  selector: 'app-health-dashboard',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './health-dashboard.component.html',
  styleUrl: './health-dashboard.component.scss',
})
export class HealthDashboardComponent implements OnInit {
  // 1. Inyección del servicio con inject()
  private readonly healthService = inject(HealthService);

  // 2. Estado del componente con signals
  services = signal<ServiceHealth[]>([]);
  loading = signal(false);
  lastChecked = signal<Date | null>(null);

  ngOnInit(): void {
    this.verificar();
  }

  verificar(): void {
    this.loading.set(true);

    // Estado inicial: todos en 'loading' mientras llegan las respuestas
    this.services.set(
      ['usuarios', 'busquedas', 'hoteles',
       'reservas', 'notificaciones'].map((name) => ({
        name,
        status: 'loading' as const,
        responseTime: null,
      }))
    );

    // 3. Suscripción al Observable que devuelve el servicio
    this.healthService.checkAll().subscribe({
      next: (results) => {
        this.services.set(results);
        this.lastChecked.set(new Date());
        this.loading.set(false);
      },
      error: () => {
        this.loading.set(false);
      },
    });
  }

  get healthyCount(): number {
    return this.services().filter((s) => s.status === 'healthy').length;
  }

  get totalCount(): number {
    return this.services().length;
  }
}
