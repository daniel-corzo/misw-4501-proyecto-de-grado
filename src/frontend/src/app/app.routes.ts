import { Routes } from '@angular/router';
import { MainLayoutComponent } from './layout/main-layout/main-layout.component';
import { AuthLayoutComponent } from './layout/auth-layout/auth-layout.component';

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
    ],
  },

  // ── Auth shell (solo logo + card centrada) ───────────────────────
  {
    path: 'auth',
    component: AuthLayoutComponent,
    children: [
      {
        path: 'login',
        loadComponent: () =>
          import('./features/auth/login/login.component').then(
            (m) => m.LoginComponent
          ),
      },
      {
        path: 'register',
        loadComponent: () =>
          import('./features/auth/register/register.component').then(
            (m) => m.RegisterComponent
          ),
      },
      { path: '', redirectTo: 'login', pathMatch: 'full' },
    ],
  },
];
