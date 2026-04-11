import { AbstractControl, ValidationErrors, ValidatorFn } from '@angular/forms';

/**
 * Validates password strength:
 * - At least 8 characters
 * - At least one uppercase letter
 * - At least one lowercase letter
 * - At least one special character
 */
export function passwordStrengthValidator(): ValidatorFn {
  return (control: AbstractControl): ValidationErrors | null => {
    const value: string = control.value ?? '';

    if (!value) return null;

    const hasMinLength = value.length >= 8;
    const hasUppercase = /[A-Z]/.test(value);
    const hasLowercase = /[a-z]/.test(value);
    const hasSpecial = /[^a-zA-Z0-9]/.test(value);

    if (hasMinLength && hasUppercase && hasLowercase && hasSpecial) {
      return null;
    }

    const missing: string[] = [];
    if (!hasMinLength) missing.push('mínimo 8 caracteres');
    if (!hasUppercase) missing.push('una letra mayúscula');
    if (!hasLowercase) missing.push('una letra minúscula');
    if (!hasSpecial) missing.push('un carácter especial');

    return { passwordStrength: { message: `La contraseña debe tener ${missing.join(', ')}` } };
  };
}
