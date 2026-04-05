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
  rooms: any[] = [];
  loading = false;

  private api = inject(ApiService);
  private toast = inject(ToastService);

  ngOnInit() {
    this.loadRooms();
  }

  loadRooms() {
    this.loading = true;
    this.api.get<any[]>('/hoteles/habitaciones').subscribe({
      next: (data) => {
        this.rooms = data;
        this.loading = false;
      },
      error: () => {
        this.toast.danger('Error al cargar los hospedajes.');
        this.loading = false;
      }
    });
  }

  openFormModal() {
    this.isFormModalOpen = true;
  }

  closeFormModal() {
    this.isFormModalOpen = false;
    this.loadRooms();
  }
}

