import { Component, inject } from '@angular/core';
import { ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';

import { AuthService } from '../../../core/services/auth.service';
import { ToastService } from '../../../core/services/toast.service';
import { passwordStrengthValidator } from '../../../shared/validators/password.validator';

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [ReactiveFormsModule],
  templateUrl: './register.component.html',
  styleUrl: './register.component.scss',
})
export class RegisterComponent {
  readonly auth = inject(AuthService);
  private readonly toast = inject(ToastService);
  private readonly fb = inject(FormBuilder);

  loading = false;
  showPassword = false;

  registerForm = this.fb.nonNullable.group({
    email:    ['', [Validators.required, Validators.email]],
    password: ['', [Validators.required, passwordStrengthValidator()]],
    nombre:   ['', [Validators.required]],
    telefono: ['', [Validators.required]],
    consent:  [false, [Validators.requiredTrue]],
  });

  get emailError(): string | null {
    const ctrl = this.registerForm.get('email');
    if (!ctrl?.invalid || !ctrl.touched) return null;
    if (ctrl.errors?.['required']) return 'El correo es requerido';
    if (ctrl.errors?.['email']) return 'Ingresa un correo válido';
    return null;
  }

  get passwordError(): string | null {
    const ctrl = this.registerForm.get('password');
    if (!ctrl?.invalid || !ctrl.touched) return null;
    if (ctrl.errors?.['required']) return 'La contraseña es requerida';
    if (ctrl.errors?.['passwordStrength']) return ctrl.errors['passwordStrength'].message;
    return null;
  }

  get nombreError(): string | null {
    const ctrl = this.registerForm.get('nombre');
    if (!ctrl?.invalid || !ctrl.touched) return null;
    return 'El nombre es requerido';
  }

  get telefonoError(): string | null {
    const ctrl = this.registerForm.get('telefono');
    if (!ctrl?.invalid || !ctrl.touched) return null;
    return 'El teléfono es requerido';
  }

  onSubmit(): void {
    if (this.registerForm.invalid || this.loading) {
      this.registerForm.markAllAsTouched();
      return;
    }

    this.loading = true;
    const { email, password, nombre, telefono } = this.registerForm.getRawValue();

    this.auth.register({
      email,
      password,
      nombre,
      telefono,
      tipo: 'viajero',
    }).subscribe({
      next: () => {
        this.toast.success('Cuenta creada exitosamente. ¡Bienvenido a TravelHub!');
        this.auth.closeRegisterModal();
        this.auth.openLoginModal();
      },
      error: (err) => {
        this.loading = false;
        const detail = err?.error?.detail;
        if (detail === 'Usuario ya existe con este email') {
          this.toast.danger('Ya existe una cuenta con ese correo');
        } else {
          this.toast.danger('No se pudo crear la cuenta, intenta más tarde');
        }
      },
    });
  }

  onCancel(): void {
    this.auth.closeRegisterModal();
  }
}
