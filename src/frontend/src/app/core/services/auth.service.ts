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

const TOKEN_KEY = 'travelhub_token';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly api = inject(ApiService);

  private readonly tokenSignal = signal<string | null>(localStorage.getItem(TOKEN_KEY));

  readonly isAuthenticated = computed(() => !!this.tokenSignal());

  readonly showLoginModal = signal(false);
  readonly showRegisterModal = signal(false);

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

  login(email: string, password: string): Observable<LoginResponse> {
    return this.api.post<LoginResponse>('/auth/login', { email, password }).pipe(
      tap((res) => {
        localStorage.setItem(TOKEN_KEY, res.access_token);
        this.tokenSignal.set(res.access_token);
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
    this.tokenSignal.set(null);
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
