import { Component, OnInit, inject } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { CommonModule } from '@angular/common';
import { HotelService, HotelDetalle, HabitacionDetalle } from '../../../core/services/hotel.service';
import { AmenitiesTagsComponent } from '../components/amenities-tags/amenities-tags.component';

@Component({
  selector: 'app-hotel-detail',
  standalone: true,
  imports: [CommonModule, RouterLink, AmenitiesTagsComponent],
  templateUrl: './hotel-detail.component.html',
  styleUrls: ['./hotel-detail.component.scss'],
})
export class HotelDetailComponent implements OnInit {
  private readonly route = inject(ActivatedRoute);
  private readonly hotelService = inject(HotelService);

  hotel: HotelDetalle | null = null;
  loading = true;
  error: string | null = null;
  selectedImageIndex = 0;
  selectedRoom: HabitacionDetalle | null = null;

  ngOnInit(): void {
    this.route.paramMap.subscribe((params) => {
      const id = params.get('id');
      this.resetHotelState();
      if (!id) {
        this.error = 'Hotel no encontrado.';
        this.loading = false;
        return;
      }
      this.loadHotel(id);
    });
  }

  private resetHotelState(): void {
    this.hotel = null;
    this.error = null;
    this.loading = true;
    this.selectedImageIndex = 0;
    this.selectedRoom = null;
  }
  private loadHotel(id: string): void {

    this.hotelService.getHotelById(id).subscribe({
      next: (hotel) => {
        this.hotel = hotel;
        if (hotel.habitaciones.length > 0) {
          this.selectedRoom = hotel.habitaciones.find(h => h.disponible) ?? hotel.habitaciones[0];
        }
        this.loading = false;
      },
      error: (err) => {
        if (err.status === 404) {
          this.error = 'El hotel solicitado no existe.';
        } else {
          this.error = 'No se pudo cargar la información del hotel. Intente de nuevo más tarde.';
        }
        this.loading = false;
      },
    });
  }

  selectImage(index: number): void {
    this.selectedImageIndex = index;
  }

  selectRoom(room: HabitacionDetalle): void {
    this.selectedRoom = room;
  }

  get minPrice(): number {
    if (!this.hotel) return 0;
    const available = this.hotel.habitaciones.filter(h => h.disponible);
    if (available.length === 0) return 0;
    return Math.min(...available.map(h => h.monto));
  }

  get starsArray(): number[] {
    return Array.from({ length: this.hotel?.estrellas ?? 0 });
  }

  formatPrice(amount: number): string {
    return amount.toLocaleString('es-CO');
  }
}
