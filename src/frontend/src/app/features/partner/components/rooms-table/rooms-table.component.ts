import { Component, ViewEncapsulation, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RoomFormModalComponent } from '../room-form-modal/room-form-modal.component';
import { ApiService } from '../../../../core/services/api.service';
import { ToastService } from '../../../../core/services/toast.service';
import { HabitacionDetalle, HotelService } from '../../../../core/services/hotel.service';
import { ModalComponent } from '../../../../shared/components/modal/modal.component';

interface ListaHabitacionesResponse {
  total: number;
  habitaciones: HabitacionDetalle[];
}

@Component({
  selector: 'app-rooms-table',
  standalone: true,
  imports: [CommonModule, RoomFormModalComponent, ModalComponent],
  templateUrl: './rooms-table.component.html',
  styleUrl: './rooms-table.component.scss',
  encapsulation: ViewEncapsulation.None,
})
export class RoomsTableComponent implements OnInit {
  isFormModalOpen = false;
  selectedRoom: HabitacionDetalle | null = null;
  rooms: HabitacionDetalle[] = [];
  loading = false;
  deleting = false;
  confirmTarget: HabitacionDetalle | null = null;

  // Pagination variables
  totalItems = 0;
  limit = 10;
  offset = 0;
  currentPage = 1;

  private api = inject(ApiService);
  private hotelService = inject(HotelService);
  private toast = inject(ToastService);

  ngOnInit() {
    this.loadRooms();
  }

  loadRooms() {
    this.loading = true;
    this.api.get<ListaHabitacionesResponse | HabitacionDetalle[]>('/hoteles/habitaciones', { limit: this.limit, offset: this.offset }).subscribe({
      next: (data) => {
        if (Array.isArray(data)) {
          this.rooms = data;
          this.totalItems = data.length;
        } else {
          this.rooms = data.habitaciones || [];
          this.totalItems = data.total || this.rooms.length;
        }
        this.loading = false;
      },
      error: (body) => {
        const errorMsg = body?.error?.detail || 'Error desconocido';
        this.toast.danger('Error al cargar los hospedajes. ' + errorMsg);
        this.loading = false;
      }
    });
  }

  changePage(page: number) {
    if (page < 1 || page > this.totalPages) return;
    this.currentPage = page;
    this.offset = (page - 1) * this.limit;
    this.loadRooms();
  }

  changeLimit(event: any) {
    this.limit = Number(event.target?.value || 10);
    this.currentPage = 1;
    this.offset = 0;
    this.loadRooms();
  }

  get totalPages(): number {
    return Math.ceil(this.totalItems / this.limit);
  }

  openFormModal() {
    this.selectedRoom = null;
    this.isFormModalOpen = true;
  }

  openEditModal(room: HabitacionDetalle) {
    this.selectedRoom = room;
    this.isFormModalOpen = true;
  }

  closeFormModal() {
    this.isFormModalOpen = false;
    this.selectedRoom = null;
    this.loadRooms();
  }

  openConfirm(room: HabitacionDetalle) {
    this.confirmTarget = room;
  }

  onDeleteRequestedFromModal(room: HabitacionDetalle) {
    this.isFormModalOpen = false;
    this.selectedRoom = null;
    this.confirmTarget = room;
  }

  cancelConfirm() {
    this.confirmTarget = null;
  }

  confirmDelete() {
    const room = this.confirmTarget;
    if (!room) return;

    this.deleting = true;
    this.hotelService.deleteRoom(room.id).subscribe({
      next: () => {
        this.toast.success(`Hospedaje "${room.numero}" eliminado exitosamente.`);
        this.confirmTarget = null;
        this.deleting = false;
        this.loadRooms();
      },
      error: (err) => {
        const detail = err?.error?.detail || 'No se pudo eliminar el hospedaje.';
        this.toast.danger(detail);
        this.confirmTarget = null;
        this.deleting = false;
      },
    });
  }
}
