import { Component, inject, HostListener, ElementRef, DestroyRef } from '@angular/core';
import { RouterLink, RouterLinkActive, Router, NavigationStart } from '@angular/router';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { filter } from 'rxjs';
import { AuthService } from '../../../core/services/auth.service';

@Component({
  selector: 'app-navbar',
  standalone: true,
  imports: [RouterLink, RouterLinkActive],
  templateUrl: './navbar.component.html',
  styleUrl: './navbar.component.scss',
})
export class NavbarComponent {
  readonly auth = inject(AuthService);
  private readonly router = inject(Router);
  private readonly el = inject(ElementRef);

  menuOpen = false;

  constructor() {
    this.router.events
      .pipe(filter((e) => e instanceof NavigationStart), takeUntilDestroyed())
      .subscribe(() => (this.menuOpen = false));
  }

  private readonly roleLabels: Record<string, string> = {
    USER: 'Viajero',
    MANAGER: 'Manager',
    ADMIN: 'Administrador',
  };

  get userRoleLabel(): string {
    const role = this.auth.getUserRole();
    return role ? (this.roleLabels[role] ?? role) : '';
  }

  get isAdminOrManager(): boolean {
    const role = this.auth.getUserRole();
    return role === 'ADMIN' || role === 'MANAGER';
  }

  toggleMenu(): void {
    this.menuOpen = !this.menuOpen;
  }

  @HostListener('document:click', ['$event'])
  onDocumentClick(event: MouseEvent): void {
    if (!this.el.nativeElement.contains(event.target)) {
      this.menuOpen = false;
    }
  }

  onLogout(): void {
    this.menuOpen = false;
    this.auth.logout().subscribe({
      complete: () => this.router.navigate(['/']),
      error: () => {
        // Si falla el endpoint, limpiamos sesión igualmente
        this.auth.clearSession();
        this.router.navigate(['/']);
      },
    });
  }
}
