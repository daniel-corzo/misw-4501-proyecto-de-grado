import { Injectable, inject, signal, computed } from '@angular/core';
import { Observable, tap } from 'rxjs';
import { ApiService } from './api.service';

interface LoginResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}

interface RegisterRequest {
  email: string;
  password: string;
  nombre: string;
  telefono?: string;
  tipo: string;
}

interface RegisterResponse {
  id: string;
  email: string;
  tipo: string;
  role: string;
}

interface UserProfile {
  id: string;
  tipo: string;
  email: string;
  role: string;
  viajero: { id: string; nombre: string; contacto: string | null } | null;
}

const TOKEN_KEY = 'travelhub_token';
const PROFILE_KEY = 'travelhub_profile';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly api = inject(ApiService);

  private readonly tokenSignal = signal<string | null>(localStorage.getItem(TOKEN_KEY));
  readonly userProfile = signal<UserProfile | null>(this.loadStoredProfile());

  readonly isAuthenticated = computed(() => !!this.tokenSignal());

  readonly userName = computed(() => {
    const p = this.userProfile();
    return p?.viajero?.nombre ?? p?.email ?? null;
  });

  readonly userInitials = computed(() => {
    const name = this.userName();
    if (!name) return '?';
    return name
      .split(' ')
      .filter(Boolean)
      .slice(0, 2)
      .map((w) => w[0].toUpperCase())
      .join('');
  });

  readonly showLoginModal = signal(false);
  readonly showRegisterModal = signal(false);

  constructor() {
    if (this.tokenSignal()) {
      this.fetchProfile();
    }
  }

  get token(): string | null {
    return this.tokenSignal();
  }

  getUserRole(): string | null {
    const token = this.tokenSignal();
    if (!token) return null;
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      return payload.role ?? null;
    } catch {
      return null;
    }
  }

  fetchProfile(): void {
    this.api.get<UserProfile>('/usuarios/me').subscribe({
      next: (profile) => {
        localStorage.setItem(PROFILE_KEY, JSON.stringify(profile));
        this.userProfile.set(profile);
      },
      error: () => {},
    });
  }

  private loadStoredProfile(): UserProfile | null {
    try {
      const raw = localStorage.getItem(PROFILE_KEY);
      return raw ? JSON.parse(raw) : null;
    } catch {
      return null;
    }
  }

  login(email: string, password: string): Observable<LoginResponse> {
    return this.api.post<LoginResponse>('/auth/login', { email, password }).pipe(
      tap((res) => {
        localStorage.setItem(TOKEN_KEY, res.access_token);
        this.tokenSignal.set(res.access_token);
        this.fetchProfile();
      }),
    );
  }

  logout(): Observable<{ message: string }> {
    return this.api.post<{ message: string }>('/auth/logout', {}).pipe(
      tap(() => this.clearSession()),
    );
  }

  clearSession(): void {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(PROFILE_KEY);
    this.tokenSignal.set(null);
    this.userProfile.set(null);
  }

  register(data: RegisterRequest): Observable<RegisterResponse> {
    return this.api.post<RegisterResponse>('/usuarios', data);
  }

  openLoginModal(): void {
    this.showLoginModal.set(true);
  }

  closeLoginModal(): void {
    this.showLoginModal.set(false);
  }

  openRegisterModal(): void {
    this.showRegisterModal.set(true);
  }

  closeRegisterModal(): void {
    this.showRegisterModal.set(false);
  }
}
