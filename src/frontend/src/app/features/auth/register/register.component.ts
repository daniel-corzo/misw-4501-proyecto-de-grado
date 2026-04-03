import { Component, inject } from '@angular/core';
import { ReactiveFormsModule, FormBuilder, Validators, FormArray } from '@angular/forms';

import { AuthService } from '../../../core/services/auth.service';
import { ToastService } from '../../../core/services/toast.service';
import { passwordStrengthValidator } from '../../../shared/validators/password.validator';
import { AmenitiesTagsComponent } from '../../hotels/components/amenities-tags/amenities-tags.component';

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [ReactiveFormsModule, AmenitiesTagsComponent],
  templateUrl: './register.component.html',
  styleUrl: './register.component.scss',
})
export class RegisterComponent {
  readonly auth = inject(AuthService);
  private readonly toast = inject(ToastService);
  private readonly fb = inject(FormBuilder);

  activeRole: 'traveler' | 'partner' = 'traveler';
  loading = false;
  showPassword = false;

  readonly travelerForm = this.fb.nonNullable.group({
    email:    ['', [Validators.required, Validators.email]],
    password: ['', [Validators.required, passwordStrengthValidator()]],
    nombre:   ['', [Validators.required]],
    telefono: ['', [Validators.required]],
    consent:  [false, [Validators.requiredTrue]],
  });

  readonly partnerForm = this.fb.nonNullable.group({
    email:        ['', [Validators.required, Validators.email]],
    password:     ['', [Validators.required, passwordStrengthValidator()]],
    nombre:    ['', [Validators.required]],
    estrellas: [0, [Validators.required]],
    descripcion: ['', [Validators.required]],
    pais:      ['', [Validators.required]],
    departamento: ['', [Validators.required]],
    ciudad:     ['', [Validators.required]],
    direccion:  ['', [Validators.required]],
    contacto_celular: ['', [Validators.required]],
    contacto_email: ['', [Validators.required, Validators.email]],
    check_in: ['', [Validators.required]],
    check_out: ['', [Validators.required]],
    valor_minimo_modificacion: [0],
    amenidades: [''],
    imagenes: this.fb.array([
      this.fb.control('', [Validators.required, Validators.pattern(/^(https?:\/\/.*\.(?:png|jpg|jpeg|gif|svg))$/i)])
    ]),
    consent:      [false, [Validators.requiredTrue]],
  });

  get registerForm() {
    return this.activeRole === 'traveler' ? this.travelerForm : this.partnerForm;
  }

  get emailError(): string | null {
    const ctrl = this.activeRole === 'traveler'
      ? this.travelerForm.controls.email
      : this.partnerForm.controls.email;
    if (!ctrl?.invalid || !ctrl.touched) return null;
    if (ctrl.errors?.['required']) return 'El correo es requerido';
    if (ctrl.errors?.['email']) return 'Ingresa un correo válido';
    return null;
  }

  get passwordError(): string | null {
    const ctrl = this.activeRole === 'traveler'
      ? this.travelerForm.controls.password
      : this.partnerForm.controls.password;
    if (!ctrl?.invalid || !ctrl.touched) return null;
    if (ctrl.errors?.['required']) return 'La contraseña es requerida';
    if (ctrl.errors?.['passwordStrength']) return ctrl.errors['passwordStrength'].message;
    return null;
  }

  get nombreError(): string | null {
    const ctrl = this.travelerForm.get('nombre');
    if (!ctrl?.invalid || !ctrl.touched) return null;
    return 'El nombre es requerido';
  }

  get telefonoError(): string | null {
    const ctrl = this.travelerForm.get('telefono');
    if (!ctrl?.invalid || !ctrl.touched) return null;
    return 'El teléfono es requerido';
  }

  get hotelNameError(): string | null {
    const ctrl = this.partnerForm.get('nombre');
    if (!ctrl?.invalid || !ctrl.touched) return null;
    return 'El nombre del hotel es requerido';
  }

  get rankingError(): string | null {
    const ctrl = this.partnerForm.get('estrellas');
    if (!ctrl?.invalid || !ctrl.touched) return null;
    if (ctrl.errors?.['required']) return 'El ranking es requerido';
    if (ctrl.errors?.['min'] || ctrl.errors?.['max']) return 'El ranking debe ser entre 1 y 5';
    return null;
  }

  get contactPhoneError(): string | null {
    const ctrl = this.partnerForm.get('contacto_celular');
    if (!ctrl?.invalid || !ctrl.touched) return null;
    return 'El teléfono de contacto es requerido';
  }

  get contactEmailError(): string | null {
    const ctrl = this.partnerForm.get('contacto_email');
    if (!ctrl?.invalid || !ctrl.touched) return null;
    if (ctrl.errors?.['required']) return 'El correo de contacto es requerido';
    if (ctrl.errors?.['email']) return 'Ingresa un correo de contacto válido';
    return null;
  }

  get descripcionError(): string | null {
    const ctrl = this.partnerForm.get('descripcion');
    if (!ctrl?.invalid || !ctrl.touched) return null;
    return 'La descripción es requerida';
  }

  get paisError(): string | null {
    const ctrl = this.partnerForm.get('pais');
    if (!ctrl?.invalid || !ctrl.touched) return null;
    return 'El país es requerido';
  }

  get departamentoError(): string | null {
    const ctrl = this.partnerForm.get('departamento');
    if (!ctrl?.invalid || !ctrl.touched) return null;
    return 'El departamento es requerido';
  }

  get ciudadError(): string | null {
    const ctrl = this.partnerForm.get('ciudad');
    if (!ctrl?.invalid || !ctrl.touched) return null;
    return 'La ciudad es requerida';
  }

  get direccionError(): string | null {
    const ctrl = this.partnerForm.get('direccion');
    if (!ctrl?.invalid || !ctrl.touched) return null;
    return 'La dirección es requerida';
  }

  get checkInError(): string | null {
    const ctrl = this.partnerForm.get('check_in');
    if (!ctrl?.invalid || !ctrl.touched) return null;
    return 'La hora de check-in es requerida';
  }

  get checkOutError(): string | null {
    const ctrl = this.partnerForm.get('check_out');
    if (!ctrl?.invalid || !ctrl.touched) return null;
    return 'La hora de check-out es requerida';
  }

  get modificationValueError(): string | null {
    const ctrl = this.partnerForm.get('valor_minimo_modificacion');
    if (!ctrl?.invalid || !ctrl.touched) return null;
    if (ctrl.errors?.['required']) return 'El valor mínimo de modificación es requerido';
    if (ctrl.errors?.['min']) return 'El valor mínimo de modificación no puede ser negativo';
    return null; 
  }

  get imagenesControls() {
    return (this.partnerForm.get('imagenes') as FormArray).controls;
  }

  get imagenesError(): string | null {
    const array = this.partnerForm.get('imagenes') as FormArray;
    if (array.invalid && array.touched) {
      for (const ctrl of array.controls) {
        if (ctrl.errors?.['required'] && ctrl.touched) return 'Al menos una imagen es requerida';
        if (ctrl.errors?.['pattern'] && ctrl.touched) return 'Ingresa URLs válidas para las imágenes';
      }
    }
    return null;
  }

  get amenitiesError(): string | null {
    const ctrl = this.partnerForm.get('amenidades');
    if (!ctrl?.invalid || !ctrl.touched) return null;
    return 'Selecciona al menos una amenidad';
  }

  onImageInput(index: number) {
    const array = this.partnerForm.get('imagenes') as FormArray;
    if (index === array.length - 1 && array.at(index).value) {
      array.push(this.fb.control('', [Validators.pattern(/^(https?:\/\/.*\.(?:png|jpg|jpeg|gif|svg))$/i)]));
    }
  }

  onSubmit(): void {
    if (this.registerForm.invalid || this.loading) {
      this.registerForm.markAllAsTouched();
      return;
    }

    this.loading = true;

    this.auth.register(this.buildRegisterPayload()).subscribe({
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

  private buildRegisterPayload(): any {
    if (this.activeRole === 'traveler') {
      const { email, password, nombre, telefono } = this.travelerForm.getRawValue();
      return {
        email,
        password,
        nombre,
        telefono,
        tipo: 'viajero',
      };
    }

    const { email, password, nombre, estrellas, descripcion, pais, departamento, ciudad, direccion, contacto_celular, check_in, check_out, valor_minimo_modificacion, amenidades, imagenes } = this.partnerForm.getRawValue();
    
    // Validate empty inputs dynamically appended
    const validImages = (imagenes as string[]).filter(img => img && img.trim() !== '');
    const amenitiesValue = typeof amenidades === 'string' ? amenidades.split(',').map(s => s.trim()).filter(s => s) : amenidades;

    return {
      email,
      password,
      nombre,
      estrellas,
      descripcion,
      pais,
      departamento,
      ciudad,
      direccion,
      contacto_celular,
      check_in,
      check_out,
      valor_minimo_modificacion,
      amenidades: amenitiesValue,
      imagenes: validImages,
      tipo: 'hotel',
    };
  }
}
