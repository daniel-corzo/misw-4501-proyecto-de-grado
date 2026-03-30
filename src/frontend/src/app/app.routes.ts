import { Routes } from '@angular/router';
import { MainLayoutComponent } from './layout/main-layout/main-layout.component';
import { authGuard } from './core/guards/auth.guard';
import { roleGuard } from './core/guards/role.guard';

export const routes: Routes = [
  // ── Authenticated shell (navbar + footer) ───────────────────────
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
        path: 'partner/dashboard',
        canActivate: [authGuard, roleGuard('MANAGER', 'ADMIN')],
        loadComponent: () =>
          import('./features/partner/dashboard.component').then(
            (m) => m.PartnerDashboardComponent
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

  // ── 404 – página independiente (sin layout shell) ─────────────────
  {
    path: '**',
    loadComponent: () =>
      import('./features/not-found/not-found.component').then(
        (m) => m.NotFoundComponent
      ),
  },
];
