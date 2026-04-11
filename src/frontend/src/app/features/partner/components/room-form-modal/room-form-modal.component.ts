import { Component, output, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, FormArray, ReactiveFormsModule, Validators } from '@angular/forms';
import { ModalComponent } from '../../../../shared/components/modal/modal.component';
import { ApiService } from '../../../../core/services/api.service';
import { ToastService } from '../../../../core/services/toast.service';
import { HttpErrorResponse } from '@angular/common/http';

@Component({
  selector: 'app-room-form-modal',
  standalone: true,
  imports: [CommonModule, ModalComponent, ReactiveFormsModule],
  templateUrl: './room-form-modal.component.html',
  styleUrl: './room-form-modal.component.scss'
})
export class RoomFormModalComponent implements OnInit {
  closeModal = output();
  roomForm!: FormGroup;
  loading = false;

  private fb = inject(FormBuilder);
  private api = inject(ApiService);
  private toast = inject(ToastService);

  ngOnInit() {
    this.roomForm = this.fb.group({
      numero: ['', [Validators.required]],
      capacidad: ['', [Validators.required, Validators.min(1)]],
      descripcion: [''],
      impuestos: ['', [Validators.required, Validators.min(0)]],
      precio: ['', [Validators.required, Validators.min(0)]],
      imagenes: this.fb.array([
        this.fb.control('', [
          Validators.required,
          Validators.pattern(/^(https?:\/\/.*\.(?:png|jpg|jpeg|gif|svg))$/i),
        ]),
      ]),
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
    if (index === controls.length - 1 && controls[index].value.trim() !== '') {
      (this.roomForm.get('imagenes') as FormArray).push(this.fb.control('', [Validators.pattern(/^(https?:\/\/.*\.(?:png|jpg|jpeg|gif|svg))$/i)]));
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

    const payload = {
      numero: String(formValue.numero),
      capacidad: Number(formValue.capacidad),
      descripcion: formValue.descripcion || null,
      monto: Number(formValue.precio),
      impuestos: Number(formValue.impuestos),
      imagenes: validImages
    };

    this.api.post('/hoteles/habitaciones', payload).subscribe({
      next: () => {
        this.toast.success('Hospedaje guardado exitosamente');
        this.loading = false;
        this.closeModal.emit();
      },
      error: (error: HttpErrorResponse) => {
        const detail = error.error?.detail;
        if (detail) {
          this.toast.danger(detail);
        } else {
          this.toast.danger(
            'Error al guardar el hospedaje. Por favor, intenta de nuevo.',
          );
        }
        this.loading = false;
      },
    });
  }
}

