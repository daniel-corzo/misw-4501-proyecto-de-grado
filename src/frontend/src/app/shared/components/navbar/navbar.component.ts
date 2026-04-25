import { Component, inject, HostListener, ElementRef, DestroyRef } from '@angular/core';
import { NgTemplateOutlet } from '@angular/common';
import { RouterLink, RouterLinkActive, Router, NavigationStart } from '@angular/router';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { filter } from 'rxjs';
import { AuthService } from '../../../core/services/auth.service';
import { TranslocoService, TranslocoPipe } from '@jsverse/transloco';

@Component({
  selector: 'app-navbar',
  standalone: true,
  imports: [RouterLink, RouterLinkActive, TranslocoPipe, NgTemplateOutlet],
  templateUrl: './navbar.component.html',
  styleUrl: './navbar.component.scss',
})
export class NavbarComponent {
  readonly auth = inject(AuthService);
  private readonly router = inject(Router);
  private readonly el = inject(ElementRef);
  readonly translocoService = inject(TranslocoService);

  menuOpen = false;
  langMenuOpen = false;

  constructor() {
    this.router.events
      .pipe(filter((e) => e instanceof NavigationStart), takeUntilDestroyed())
      .subscribe(() => {
        this.menuOpen = false;
        this.langMenuOpen = false;
      });
  }

  get currentLang() {
    return this.translocoService.getActiveLang();
  }

  setLang(lang: string) {
    this.translocoService.setActiveLang(lang);
    if (typeof window !== 'undefined') {
      localStorage.setItem('appLang', lang);
    }
    this.langMenuOpen = false;
  }

  toggleLangMenu(event: Event): void {
    event.stopPropagation();
    this.langMenuOpen = !this.langMenuOpen;
    this.menuOpen = false;
  }

  private readonly roleTranslations: Record<string, string> = {
    viajero: 'navbar.roleTraveler',
    hotel: 'navbar.rolePartner',
  };

  get userRoleLabel(): string {
    const type = this.auth.getUserType();
    if (!type) return 'NA';
    const key = this.roleTranslations[type];
    return key ? this.translocoService.translate(key) : type;
  }

  toggleMenu(event: Event): void {
    event.stopPropagation();
    this.menuOpen = !this.menuOpen;
    this.langMenuOpen = false;
  }

  @HostListener('document:click', ['$event'])
  onDocumentClick(event: MouseEvent): void {
    if (!this.el.nativeElement.contains(event.target)) {
      this.menuOpen = false;
      this.langMenuOpen = false;
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
