import { Component, inject } from '@angular/core';
import { ReactiveFormsModule, FormBuilder, Validators, FormArray } from '@angular/forms';
import { TranslocoPipe, TranslocoService } from '@jsverse/transloco';

import { AuthService } from '../../../core/services/auth.service';
import { ToastService } from '../../../core/services/toast.service';
import { passwordStrengthValidator } from '../../../shared/validators/password.validator';
import { AmenitiesTagsComponent } from '../../hotels/components/amenities-tags/amenities-tags.component';

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [ReactiveFormsModule, AmenitiesTagsComponent, TranslocoPipe],
  templateUrl: './register.component.html',
  styleUrl: './register.component.scss',
})
export class RegisterComponent {
  readonly auth = inject(AuthService);
  private readonly toast = inject(ToastService);
  private readonly fb = inject(FormBuilder);
  private readonly t = inject(TranslocoService);

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
    estrellas: [1, [Validators.required, Validators.min(1), Validators.max(5)]],
    descripcion: ['', [Validators.required]],
    pais:      ['', [Validators.required]],
    departamento: ['', [Validators.required]],
    ciudad:     ['', [Validators.required]],
    direccion:  ['', [Validators.required]],
    contacto_celular: ['', [Validators.required]],
    contacto_email: ['', [Validators.required, Validators.email]],
    check_in: ['', [Validators.required]],
    check_out: ['', [Validators.required]],
    valor_minimo_modificacion: [0, [Validators.required, Validators.min(0)]],
    amenidades: ['', [Validators.required]],
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
    if (ctrl.errors?.['required']) return this.t.translate('auth.register.errors.emailRequired');
    if (ctrl.errors?.['email']) return this.t.translate('auth.register.errors.emailInvalid');
    return null;
  }

  get passwordError(): string | null {
    const ctrl = this.activeRole === 'traveler'
      ? this.travelerForm.controls.password
      : this.partnerForm.controls.password;
    if (!ctrl?.invalid || !ctrl.touched) return null;
    if (ctrl.errors?.['required']) return this.t.translate('auth.register.errors.passwordRequired');
    if (ctrl.errors?.['passwordStrength']) {
      const keys: string[] = ctrl.errors['passwordStrength'].keys;
      const translated = keys.map((k: string) => this.t.translate(k));
      return this.t.translate('auth.register.errors.passwordStrengthPrefix') + ' ' + translated.join(', ');
    }
    return null;
  }

  get nombreError(): string | null {
    const ctrl = this.travelerForm.get('nombre');
    if (!ctrl?.invalid || !ctrl.touched) return null;
    return this.t.translate('auth.register.errors.nameRequired');
  }

  get telefonoError(): string | null {
    const ctrl = this.travelerForm.get('telefono');
    if (!ctrl?.invalid || !ctrl.touched) return null;
    return this.t.translate('auth.register.errors.phoneRequired');
  }

  get hotelNameError(): string | null {
    const ctrl = this.partnerForm.get('nombre');
    if (!ctrl?.invalid || !ctrl.touched) return null;
    return this.t.translate('auth.register.errors.hotelNameRequired');
  }

  get rankingError(): string | null {
    const ctrl = this.partnerForm.get('estrellas');
    if (!ctrl?.invalid || !ctrl.touched) return null;
    if (ctrl.errors?.['required']) return this.t.translate('auth.register.errors.rankingRequired');
    if (ctrl.errors?.['min'] || ctrl.errors?.['max']) return this.t.translate('auth.register.errors.rankingInvalid');
    return null;
  }

  get contactPhoneError(): string | null {
    const ctrl = this.partnerForm.get('contacto_celular');
    if (!ctrl?.invalid || !ctrl.touched) return null;
    return this.t.translate('auth.register.errors.contactPhoneRequired');
  }

  get contactEmailError(): string | null {
    const ctrl = this.partnerForm.get('contacto_email');
    if (!ctrl?.invalid || !ctrl.touched) return null;
    if (ctrl.errors?.['required']) return this.t.translate('auth.register.errors.contactEmailRequired');
    if (ctrl.errors?.['email']) return this.t.translate('auth.register.errors.contactEmailInvalid');
    return null;
  }

  get descripcionError(): string | null {
    const ctrl = this.partnerForm.get('descripcion');
    if (!ctrl?.invalid || !ctrl.touched) return null;
    return this.t.translate('auth.register.errors.descriptionRequired');
  }

  get paisError(): string | null {
    const ctrl = this.partnerForm.get('pais');
    if (!ctrl?.invalid || !ctrl.touched) return null;
    return this.t.translate('auth.register.errors.countryRequired');
  }

  get departamentoError(): string | null {
    const ctrl = this.partnerForm.get('departamento');
    if (!ctrl?.invalid || !ctrl.touched) return null;
    return this.t.translate('auth.register.errors.stateRequired');
  }

  get ciudadError(): string | null {
    const ctrl = this.partnerForm.get('ciudad');
    if (!ctrl?.invalid || !ctrl.touched) return null;
    return this.t.translate('auth.register.errors.cityRequired');
  }

  get direccionError(): string | null {
    const ctrl = this.partnerForm.get('direccion');
    if (!ctrl?.invalid || !ctrl.touched) return null;
    return this.t.translate('auth.register.errors.addressRequired');
  }

  get checkInError(): string | null {
    const ctrl = this.partnerForm.get('check_in');
    if (!ctrl?.invalid || !ctrl.touched) return null;
    return this.t.translate('auth.register.errors.checkInRequired');
  }

  get checkOutError(): string | null {
    const ctrl = this.partnerForm.get('check_out');
    if (!ctrl?.invalid || !ctrl.touched) return null;
    return this.t.translate('auth.register.errors.checkOutRequired');
  }

  get modificationValueError(): string | null {
    const ctrl = this.partnerForm.get('valor_minimo_modificacion');
    if (!ctrl?.invalid || !ctrl.touched) return null;
    if (ctrl.errors?.['required']) return this.t.translate('auth.register.errors.modificationValueRequired');
    if (ctrl.errors?.['min']) return this.t.translate('auth.register.errors.modificationValueNegative');
    return null; 
  }

  get imagenesControls() {
    return (this.partnerForm.get('imagenes') as FormArray).controls;
  }

  get imagenesError(): string | null {
    const array = this.partnerForm.get('imagenes') as FormArray;
    if (array.invalid && array.touched) {
      for (const ctrl of array.controls) {
        if (ctrl.errors?.['required'] && ctrl.touched) return this.t.translate('auth.register.errors.imageRequired');
        if (ctrl.errors?.['pattern'] && ctrl.touched) return this.t.translate('auth.register.errors.imageInvalid');
      }
    }
    return null;
  }

  get amenitiesError(): string | null {
    const ctrl = this.partnerForm.get('amenidades');
    if (!ctrl?.invalid || !ctrl.touched) return null;
    return this.t.translate('auth.register.errors.amenityRequired');
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
        this.toast.success(this.t.translate('auth.register.success'));
        this.auth.closeRegisterModal();
        this.auth.openLoginModal();
      },
      error: (err) => {
        this.loading = false;
        const detail = err?.error?.detail;
        if (detail === 'Usuario ya existe con este email') {
          this.toast.danger(this.t.translate('auth.register.emailExists'));
        } else {
          this.toast.danger(this.t.translate('auth.register.createError'));
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

    const { email, password, nombre, estrellas, descripcion, pais, departamento, ciudad, direccion, contacto_celular, contacto_email, check_in, check_out, valor_minimo_modificacion, amenidades, imagenes } = this.partnerForm.getRawValue();
    
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
      contacto_email,
      check_in,
      check_out,
      valor_minimo_modificacion,
      amenidades: amenitiesValue,
      imagenes: validImages,
      tipo: 'hotel',
    };
  }
}
