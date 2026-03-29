import { Injectable, inject, signal, computed } from '@angular/core';
import { Router } from '@angular/router';
import { Observable, tap } from 'rxjs';
import { ApiService } from './api.service';

interface LoginResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}

const TOKEN_KEY = 'travelhub_token';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly api = inject(ApiService);
  private readonly router = inject(Router);

  private readonly tokenSignal = signal<string | null>(localStorage.getItem(TOKEN_KEY));

  readonly isAuthenticated = computed(() => !!this.tokenSignal());

  get token(): string | null {
    return this.tokenSignal();
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
    this.router.navigate(['/auth/login']);
  }
}
