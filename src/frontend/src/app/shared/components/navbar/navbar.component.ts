import { Component, inject, HostListener, ElementRef } from '@angular/core';
import { RouterLink, RouterLinkActive, Router } from '@angular/router';
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
