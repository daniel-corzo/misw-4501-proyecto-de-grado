import { Component, effect, inject, input, output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, FormArray, ReactiveFormsModule, Validators } from '@angular/forms';
import { ModalComponent } from '../../../../shared/components/modal/modal.component';
import { ApiService } from '../../../../core/services/api.service';
import { ToastService } from '../../../../core/services/toast.service';
import { HttpErrorResponse } from '@angular/common/http';
import { HabitacionDetalle } from '../../../../core/services/hotel.service';
import { TranslocoPipe, TranslocoService } from '@jsverse/transloco';

@Component({
  selector: 'app-room-form-modal',
  standalone: true,
  imports: [CommonModule, ModalComponent, ReactiveFormsModule, TranslocoPipe],
  templateUrl: './room-form-modal.component.html',
  styleUrl: './room-form-modal.component.scss'
})
export class RoomFormModalComponent {
  room = input<HabitacionDetalle | null>(null);
  closeModal = output();
  deleteRequested = output<HabitacionDetalle>();
  roomForm: FormGroup;
  loading = false;

  private fb = inject(FormBuilder);
  private api = inject(ApiService);
  private toast = inject(ToastService);
  private t = inject(TranslocoService);
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
    return this.isEditMode ? this.t.translate('partner.roomForm.editTitle') : this.t.translate('partner.roomForm.createTitle');
  }

  get submitLabel(): string {
    if (this.loading) {
      return this.isEditMode ? this.t.translate('partner.roomForm.savingEdit') : this.t.translate('partner.roomForm.saving');
    }

    return this.isEditMode ? this.t.translate('partner.roomForm.saveEdit') : this.t.translate('partner.roomForm.save');
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
    return this.t.translate('partner.roomForm.errors.numberRequired');
  }

  get capacidadError(): string | null {
    const ctrl = this.roomForm.get('capacidad');
    if (!ctrl?.invalid || !ctrl.touched) return null;
    if (ctrl.errors?.['required']) return this.t.translate('partner.roomForm.errors.capacityRequired');
    if (ctrl.errors?.['min']) return this.t.translate('partner.roomForm.errors.capacityMin');
    return null;
  }

  get impuestosError(): string | null {
    const ctrl = this.roomForm.get('impuestos');
    if (!ctrl?.invalid || !ctrl.touched) return null;
    if (ctrl.errors?.['required']) return this.t.translate('partner.roomForm.errors.taxesRequired');
    if (ctrl.errors?.['min']) return this.t.translate('partner.roomForm.errors.taxesNegative');
    return null;
  }

  get precioError(): string | null {
    const ctrl = this.roomForm.get('precio');
    if (!ctrl?.invalid || !ctrl.touched) return null;
    if (ctrl.errors?.['required']) return this.t.translate('partner.roomForm.errors.priceRequired');
    if (ctrl.errors?.['min']) return this.t.translate('partner.roomForm.errors.priceNegative');
    return null;
  }

  get imagenesError(): string | null {
    const array = this.roomForm.get('imagenes') as FormArray;
    if (array.invalid && array.touched) {
      for (const ctrl of array.controls) {
        if (ctrl.errors?.['required'] && ctrl.touched) return this.t.translate('partner.roomForm.errors.imageRequired');
        if (ctrl.errors?.['pattern'] && ctrl.touched) return this.t.translate('partner.roomForm.errors.imageInvalid');
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

  onDeleteClick() {
    const room = this.room();
    if (room) this.deleteRequested.emit(room);
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
            ? this.t.translate('partner.roomForm.successEdit')
            : this.t.translate('partner.roomForm.successCreate'),
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
              ? this.t.translate('partner.roomForm.errorEdit')
              : this.t.translate('partner.roomForm.errorCreate'),
          );
        }
        this.loading = false;
      },
    });
  }
}

