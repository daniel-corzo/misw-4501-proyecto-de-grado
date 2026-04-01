import { Routes } from '@angular/router';
import { MainLayoutComponent } from './layout/main-layout/main-layout.component';
import { AdminLayoutComponent } from './layout/admin-layout/admin-layout.component';
import { authGuard } from './core/guards/auth.guard';
import { roleGuard } from './core/guards/role.guard';

export const routes: Routes = [
  // ── Portal público (navbar + footer) ────────────────────────────
  {
    path: '',
    component: MainLayoutComponent,
    children: [
      {
        path: 'health',
        loadComponent: () =>
          import('./features/health/health-dashboard.component').then(
            (m) => m.HealthDashboardComponent
          ),
      },
      {
        path: '',
        loadComponent: () =>
          import('./features/home/home.component').then(
            (m) => m.HomeComponent
          ),
      },
      {
        path: 'settings',
        canActivate: [authGuard],
        loadComponent: () =>
          import('./features/settings/settings.component').then(
            (m) => m.SettingsComponent
          ),
      },
      {
        path: 'bookings',
        canActivate: [authGuard],
        loadComponent: () =>
          import('./features/bookings/bookings.component').then(
            (m) => m.BookingsComponent
          ),
      },
      {
        path: 'terms',
        loadComponent: () =>
          import('./features/terms/terms.component').then(
            (m) => m.TermsComponent
          ),
      },
    ],
  },

  // ── Panel de administración (layout propio con sidebar) ──────────
  {
    path: 'admin',
    component: AdminLayoutComponent,
    canActivate: [authGuard, roleGuard('ADMIN', 'MANAGER')],
    children: [
      {
        path: '',
        loadComponent: () =>
          import('./features/admin/dashboard/admin-dashboard.component').then(
            (m) => m.AdminDashboardComponent
          ),
      },
      {
        path: 'hoteles',
        loadComponent: () =>
          import('./features/admin/hoteles/admin-hoteles.component').then(
            (m) => m.AdminHotelesComponent
          ),
      },
      {
        path: 'reservas',
        loadComponent: () =>
          import('./features/admin/reservas/admin-reservas.component').then(
            (m) => m.AdminReservasComponent
          ),
      },
      {
        path: 'usuarios',
        canActivate: [roleGuard('ADMIN')],
        loadComponent: () =>
          import('./features/admin/usuarios/admin-usuarios.component').then(
            (m) => m.AdminUsuariosComponent
          ),
      },
      {
        path: 'reportes',
        loadComponent: () =>
          import('./features/admin/reportes/admin-reportes.component').then(
            (m) => m.AdminReportesComponent
          ),
      },
    ],
  },

  // ── 404 ──────────────────────────────────────────────────────────
  {
    path: '**',
    loadComponent: () =>
      import('./features/not-found/not-found.component').then(
        (m) => m.NotFoundComponent
      ),
  },
];
