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

  readonly placeholderImage = 'data:image/svg+xml;charset=UTF-8,%3Csvg xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22 width%3D%22400%22 height%3D%22300%22 viewBox%3D%220 0 400 300%22%3E%3Crect width%3D%22400%22 height%3D%22300%22 fill%3D%22%23f1f3f4%22%2F%3E%3Crect x%3D%22130%22 y%3D%2290%22 width%3D%22140%22 height%3D%22110%22 rx%3D%225%22 fill%3D%22none%22 stroke%3D%22%239aa0a6%22 stroke-width%3D%224%22%2F%3E%3Ccircle cx%3D%22160%22 cy%3D%22118%22 r%3D%2214%22 fill%3D%22none%22 stroke%3D%22%239aa0a6%22 stroke-width%3D%224%22%2F%3E%3Cpolyline points%3D%22130%2C200 165%2C162 192%2C180 215%2C163 270%2C200%22 fill%3D%22none%22 stroke%3D%22%239aa0a6%22 stroke-width%3D%224%22 stroke-linejoin%3D%22round%22 stroke-linecap%3D%22round%22%2F%3E%3C%2Fsvg%3E';

  onImageError(event: Event): void {
    const img = event.target as HTMLImageElement;
    img.src = this.placeholderImage;
  }
}
