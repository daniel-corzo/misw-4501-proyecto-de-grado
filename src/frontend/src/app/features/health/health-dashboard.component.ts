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
  // 1. Inyección del servicio con la función inject() (Angular 14+)
  private readonly healthService = inject(HealthService);

  // 2. Estado del componente con signals (Angular 16+)
  services = signal<ServiceHealth[]>([]);
  loading = signal(false);
  lastChecked = signal<Date | null>(null);

  ngOnInit(): void {
    this.verificar();
  }

  verificar(): void {
    this.loading.set(true);

    // Estado inicial: todos en 'loading'
    this.services.set(
      ['autenticacion', 'usuarios', 'busqueda', 'hoteles',
       'inventario', 'reservas', 'pagos', 'notificaciones'].map((name) => ({
        name,
        status: 'loading' as const,
        responseTime: null,
      }))
    );

    // 3. Consumo del servicio: suscripción al Observable
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
