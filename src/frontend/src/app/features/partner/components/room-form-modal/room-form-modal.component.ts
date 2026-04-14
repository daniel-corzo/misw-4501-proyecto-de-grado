import { Component, effect, inject, input, output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, FormArray, ReactiveFormsModule, Validators } from '@angular/forms';
import { ModalComponent } from '../../../../shared/components/modal/modal.component';
import { ApiService } from '../../../../core/services/api.service';
import { ToastService } from '../../../../core/services/toast.service';
import { HttpErrorResponse } from '@angular/common/http';
import { HabitacionDetalle } from '../../../../core/services/hotel.service';

@Component({
  selector: 'app-room-form-modal',
  standalone: true,
  imports: [CommonModule, ModalComponent, ReactiveFormsModule],
  templateUrl: './room-form-modal.component.html',
  styleUrl: './room-form-modal.component.scss'
})
export class RoomFormModalComponent {
  room = input<HabitacionDetalle | null>(null);
  closeModal = output();
  roomForm: FormGroup;
  loading = false;

  private fb = inject(FormBuilder);
  private api = inject(ApiService);
  private toast = inject(ToastService);
  private readonly imageUrlPattern = /^(https?:\/\/.*\.(?:png|jpg|jpeg|gif|svg))$/i;

  constructor() {
    this.roomForm = this.buildForm();

    effect(() => {
      this.syncFormWithRoom(this.room());
    });
  }

  get isEditMode(): boolean {
    return this.room() !== null;
  }

  get modalTitle(): string {
    return this.isEditMode ? 'Modifica un hospedaje' : 'Agrega un hospedaje';
  }

  get submitLabel(): string {
    if (this.loading) {
      return this.isEditMode ? 'Guardando cambios...' : 'Guardando...';
    }

    return this.isEditMode ? 'Guardar cambios' : 'Guardar hospedaje';
  }

  private buildForm(): FormGroup {
    return this.fb.group({
      numero: ['', [Validators.required]],
      capacidad: ['', [Validators.required, Validators.min(1)]],
      descripcion: [''],
      impuestos: ['', [Validators.required, Validators.min(0)]],
      precio: ['', [Validators.required, Validators.min(0)]],
      imagenes: this.fb.array([
        this.buildImageControl('', true),
      ]),
    });
  }

  private buildImageControl(value = '', required = false) {
    const validators = [Validators.pattern(this.imageUrlPattern)];
    if (required) {
      validators.unshift(Validators.required);
    }

    return this.fb.control(value, validators);
  }

  private syncFormWithRoom(room: HabitacionDetalle | null): void {
    this.roomForm.reset({
      numero: room?.numero ?? '',
      capacidad: room?.capacidad ?? '',
      descripcion: room?.descripcion ?? '',
      impuestos: room?.impuestos ?? '',
      precio: room?.monto ?? '',
    });

    this.resetImageControls(room?.imagenes ?? []);
    this.roomForm.markAsPristine();
    this.roomForm.markAsUntouched();
  }

  private resetImageControls(images: string[]): void {
    const imageArray = this.roomForm.get('imagenes') as FormArray;
    while (imageArray.length > 0) {
      imageArray.removeAt(0);
    }

    const values = images.length > 0 ? [...images, ''] : [''];
    values.forEach((value, index) => {
      imageArray.push(this.buildImageControl(value, index === 0));
    });
  }

  get imagenesControls() {
    return (this.roomForm.get('imagenes') as FormArray).controls;
  }

  get numeroError(): string | null {
    const ctrl = this.roomForm.get('numero');
    if (!ctrl?.invalid || !ctrl.touched) return null;
    return 'El número es requerido';
  }

  get capacidadError(): string | null {
    const ctrl = this.roomForm.get('capacidad');
    if (!ctrl?.invalid || !ctrl.touched) return null;
    if (ctrl.errors?.['required']) return 'La capacidad es requerida';
    if (ctrl.errors?.['min']) return 'La capacidad debe ser mayor a 0';
    return null;
  }

  get impuestosError(): string | null {
    const ctrl = this.roomForm.get('impuestos');
    if (!ctrl?.invalid || !ctrl.touched) return null;
    if (ctrl.errors?.['required']) return 'Los impuestos son requeridos';
    if (ctrl.errors?.['min']) return 'Los impuestos no pueden ser negativos';
    return null;
  }

  get precioError(): string | null {
    const ctrl = this.roomForm.get('precio');
    if (!ctrl?.invalid || !ctrl.touched) return null;
    if (ctrl.errors?.['required']) return 'El precio es requerido';
    if (ctrl.errors?.['min']) return 'El precio no puede ser negativo';
    return null;
  }

  get imagenesError(): string | null {
    const array = this.roomForm.get('imagenes') as FormArray;
    if (array.invalid && array.touched) {
      for (const ctrl of array.controls) {
        if (ctrl.errors?.['required'] && ctrl.touched) return 'Al menos una imagen es requerida';
        if (ctrl.errors?.['pattern'] && ctrl.touched) return 'Ingresa URLs válidas para las imágenes';
      }
    }
    return null;
  }

  onImageInput(index: number) {
    const controls = this.imagenesControls;
    const currentValue = String(controls[index].value ?? '').trim();
    if (index === controls.length - 1 && currentValue !== '') {
      (this.roomForm.get('imagenes') as FormArray).push(this.buildImageControl());
    }
  }

  onSubmit() {
    if (this.roomForm.invalid || this.loading) {
      this.roomForm.markAllAsTouched();
      return;
    }

    this.loading = true;
    const formValue = this.roomForm.getRawValue();
    const validImages = (formValue.imagenes as string[]).filter(img => img && img.trim() !== '');
    const currentRoom = this.room();

    const payload = {
      numero: String(formValue.numero),
      capacidad: Number(formValue.capacidad),
      descripcion: formValue.descripcion || null,
      monto: Number(formValue.precio),
      impuestos: Number(formValue.impuestos),
      imagenes: validImages,
      disponible: currentRoom?.disponible ?? true,
    };

    const request$ = currentRoom
      ? this.api.put(`/hoteles/habitaciones/${currentRoom.id}`, payload)
      : this.api.post('/hoteles/habitaciones', payload);

    request$.subscribe({
      next: () => {
        this.toast.success(
          this.isEditMode
            ? 'Hospedaje actualizado exitosamente'
            : 'Hospedaje guardado exitosamente',
        );
        this.loading = false;
        this.closeModal.emit();
      },
      error: (error: HttpErrorResponse) => {
        const detail = error.error?.detail;
        if (detail) {
          this.toast.danger(detail);
        } else {
          this.toast.danger(
            this.isEditMode
              ? 'Error al actualizar el hospedaje. Por favor, intenta de nuevo.'
              : 'Error al guardar el hospedaje. Por favor, intenta de nuevo.',
          );
        }
        this.loading = false;
      },
    });
  }
}

