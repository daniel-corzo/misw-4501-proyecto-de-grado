import { Component, inject, signal } from '@angular/core';
import { RouterOutlet, RouterLink, RouterLinkActive, Router } from '@angular/router';
import { AuthService } from '../../core/services/auth.service';

interface NavItem {
  label: string;
  path: string;
  icon: string;
  adminOnly?: boolean;
}

@Component({
  selector: 'app-admin-layout',
  standalone: true,
  imports: [RouterOutlet, RouterLink, RouterLinkActive],
  templateUrl: './admin-layout.component.html',
  styleUrl: './admin-layout.component.scss',
})
export class AdminLayoutComponent {
  readonly auth = inject(AuthService);
  private readonly router = inject(Router);

  sidebarCollapsed = signal(false);

  readonly navItems: NavItem[] = [
    { label: 'Dashboard',  path: '/admin',          icon: 'dashboard' },
    { label: 'Hoteles',    path: '/admin/hoteles',   icon: 'hotel'     },
    { label: 'Reservas',   path: '/admin/reservas',  icon: 'calendar'  },
    { label: 'Usuarios',   path: '/admin/usuarios',  icon: 'users', adminOnly: true },
    { label: 'Reportes',   path: '/admin/reportes',  icon: 'chart'     },
  ];

  get visibleNavItems(): NavItem[] {
    const role = this.auth.getUserRole();
    return this.navItems.filter(item => !item.adminOnly || role === 'ADMIN');
  }

  toggleSidebar(): void {
    this.sidebarCollapsed.update(v => !v);
  }

  onLogout(): void {
    this.auth.logout().subscribe({
      complete: () => this.router.navigate(['/']),
      error: () => {
        this.auth.clearSession();
        this.router.navigate(['/']);
      },
    });
  }
}
