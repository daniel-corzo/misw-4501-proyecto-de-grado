import { Routes } from '@angular/router';
import { HealthDashboardComponent } from './features/health/health-dashboard.component';

export const routes: Routes = [
  { path: 'health', component: HealthDashboardComponent },
  { path: '', redirectTo: 'health', pathMatch: 'full' },
];
