import { Component, OnInit, inject } from '@angular/core';
import { ActivatedRoute, ParamMap, Router, RouterLink } from '@angular/router';
import { CommonModule } from '@angular/common';
import { HttpErrorResponse } from '@angular/common/http';
import { HotelService, HotelDetalle, HabitacionDetalle } from '../../../core/services/hotel.service';
import { BookingService } from '../../../core/services/booking.service';
import { ToastService } from '../../../core/services/toast.service';
import { PLACEHOLDER_IMAGE } from '../../../shared/constants/images';
import { AmenitiesTagsComponent } from '../components/amenities-tags/amenities-tags.component';
import { TranslocoPipe, TranslocoService } from '@jsverse/transloco';

@Component({
  selector: 'app-hotel-detail',
  standalone: true,
  imports: [CommonModule, RouterLink, AmenitiesTagsComponent, TranslocoPipe],
  templateUrl: './hotel-detail.component.html',
  styleUrls: ['./hotel-detail.component.scss'],
})
export class HotelDetailComponent implements OnInit {
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);
  private readonly hotelService = inject(HotelService);
  private readonly bookingService = inject(BookingService);
  private readonly toast = inject(ToastService);
  private readonly t = inject(TranslocoService);

  hotel: HotelDetalle | null = null;
  loading = true;
  error: string | null = null;
  selectedImageIndex = 0;
  selectedRoom: HabitacionDetalle | null = null;
  reservando = false;
  fechaEntrada: string | null = null;
  fechaSalida: string | null = null;
  numHuespedes = 1;
  private readonly dateTimeFormatter = new Intl.DateTimeFormat('es-CO', {
    weekday: 'short',
    day: '2-digit',
    month: 'short',
  });

  ngOnInit(): void {
    const queryParams = this.route.snapshot.queryParamMap;
    this.fechaEntrada = queryParams.get('checkIn');
    this.fechaSalida = queryParams.get('checkOut');
    this.numHuespedes = Number(queryParams.get('huespedes') ?? '1') || 1;

    this.route.paramMap.subscribe((params: ParamMap) => {
      const id = params.get('id');
      this.resetHotelState();
      if (!id) {
        this.error = this.t.translate('hotelDetail.notFound');
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
      next: (hotel: HotelDetalle) => {
        this.hotel = hotel;
        if (hotel.habitaciones.length > 0) {
          this.selectedRoom = hotel.habitaciones.find((h: HabitacionDetalle) => h.disponible) ?? hotel.habitaciones[0];
        }
        this.loading = false;
      },
      error: (err: HttpErrorResponse) => {
        if (err.status === 404) {
          this.error = this.t.translate('hotelDetail.notFoundDetail');
        } else {
          this.error = this.t.translate('hotelDetail.loadError');
        }
        this.loading = false;
      },
    });
  }

  get puedeReservar(): boolean {
    return !!this.selectedRoom?.disponible && !!this.fechaEntrada && !!this.fechaSalida && !this.reservando;
  }

  reservarAhora(): void {
    if (!this.selectedRoom?.disponible) {
      this.toast.warning(this.t.translate('hotelDetail.toastSelectAvailableRoom'));
      return;
    }

    if (!this.fechaEntrada || !this.fechaSalida) {
      this.toast.warning(this.t.translate('hotelDetail.toastSelectDates'));
      return;
    }

    this.reservando = true;
    this.bookingService.createReservation({
      habitacion_id: this.selectedRoom.id,
      fecha_entrada: this.fechaEntrada,
      fecha_salida: this.fechaSalida,
      num_huespedes: this.numHuespedes,
      pago_id: null,
    }).subscribe({
      next: () => {
        this.toast.success(this.t.translate('hotelDetail.toastCreated'));
        this.router.navigate(['/bookings']);
      },
      error: (err: HttpErrorResponse) => {
        if (err.status === 409) {
          this.toast.warning(this.t.translate('hotelDetail.toastRoomNoLongerAvailable'));
        } else {
          this.toast.danger(this.t.translate('hotelDetail.toastCreateError'));
        }
        this.reservando = false;
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

  get stayNights(): number {
    if (!this.fechaEntrada || !this.fechaSalida) {
      return 1;
    }

    const start = this.parseDateOnly(this.fechaEntrada);
    const end = this.parseDateOnly(this.fechaSalida);
    const diffInMs = end.getTime() - start.getTime();
    const nights = Math.ceil(diffInMs / (1000 * 60 * 60 * 24));

    return Number.isFinite(nights) && nights > 0 ? nights : 1;
  }

  get roomSubtotal(): number {
    return (this.selectedRoom?.monto ?? this.minPrice) * this.stayNights;
  }

  get roomTaxes(): number {
    return this.selectedRoom?.impuestos ?? 0;
  }

  get totalPrice(): number {
    return this.roomSubtotal + this.roomTaxes;
  }

  formatCheckInOut(dateValue: string | null, timeValue: string | null): string {
    if (!dateValue && !timeValue) {
      return '--';
    }

    const parts: string[] = [];

    if (dateValue) {
      const date = this.parseDateOnly(dateValue);
      if (!Number.isNaN(date.getTime())) {
        parts.push(this.dateTimeFormatter.format(date));
      }
    }

    if (timeValue) {
      parts.push(timeValue);
    }

    return parts.join(' · ');
  }

  readonly placeholderImage = PLACEHOLDER_IMAGE;

  onImageError(event: Event): void {
    const img = event.target as HTMLImageElement;
    img.src = this.placeholderImage;
  }

  private parseDateOnly(value: string): Date {
    const match = /^(\d{4})-(\d{2})-(\d{2})$/.exec(value);
    if (!match) {
      return new Date(value);
    }

    const year = Number(match[1]);
    const monthIndex = Number(match[2]) - 1;
    const day = Number(match[3]);
    return new Date(year, monthIndex, day);
  }
}
