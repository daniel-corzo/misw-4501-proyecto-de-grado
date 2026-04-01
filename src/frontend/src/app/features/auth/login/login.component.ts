import { Component, inject } from '@angular/core';
import { ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';
import { Router } from '@angular/router';

import { AuthService } from '../../../core/services/auth.service';
import { ToastService } from '../../../core/services/toast.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [ReactiveFormsModule],
  templateUrl: './login.component.html',
  styleUrl: './login.component.scss',
})
export class LoginComponent {
  readonly auth = inject(AuthService);
  private readonly toast = inject(ToastService);
  private readonly fb = inject(FormBuilder);
  private readonly router = inject(Router);

  loading = false;
  showPassword = false;

  loginForm = this.fb.nonNullable.group({
    email: ['', [Validators.required, Validators.email]],
    password: ['', [Validators.required]],
  });

  onSubmit(): void {
    if (this.loginForm.invalid || this.loading) return;

    this.loading = true;
    const { email, password } = this.loginForm.getRawValue();

    this.auth.login(email, password).subscribe({
      next: () => {
        this.auth.closeLoginModal();
        const role = this.auth.getUserRole();
        if (role === 'ADMIN' || role === 'MANAGER') {
          this.router.navigate(['/admin']);
        }
        // USER stays on current page (home)
      },
      error: (err) => {
        this.loading = false;
        if (err?.status === 429) {
          this.toast.danger('Demasiados intentos fallidos. Intenta de nuevo en 15 minutos.');
        } else {
          this.toast.danger('Correo o contraseña incorrecta');
        }
      },
    });
  }
}
