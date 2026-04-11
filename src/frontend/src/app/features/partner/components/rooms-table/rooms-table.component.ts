import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RoomFormModalComponent } from '../room-form-modal/room-form-modal.component';
import { ApiService } from '../../../../core/services/api.service';
import { ToastService } from '../../../../core/services/toast.service';

@Component({
  selector: 'app-rooms-table',
  standalone: true,
  imports: [CommonModule, RoomFormModalComponent],
  templateUrl: './rooms-table.component.html',
  styleUrl: './rooms-table.component.scss'
})
export class RoomsTableComponent implements OnInit {
  isFormModalOpen = false;
  allRooms: any[] = [];
  rooms: any[] = [];
  loading = false;
  
  // Pagination variables
  totalItems = 0;
  limit = 10;
  offset = 0;
  currentPage = 1;

  private api = inject(ApiService);
  private toast = inject(ToastService);

  ngOnInit() {
    this.loadRooms();
  }

  loadRooms() {
    this.loading = true;
    this.api.get<any>('/hoteles/habitaciones', { "limit": this.limit, "offset": this.offset }).subscribe({
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
    this.isFormModalOpen = true;
  }

  closeFormModal() {
    this.isFormModalOpen = false;
    this.loadRooms();
  }
}

