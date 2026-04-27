import { CommonModule } from '@angular/common';
import { HttpErrorResponse } from '@angular/common/http';
import { Component, OnInit, inject } from '@angular/core';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { TranslocoPipe, TranslocoService } from '@jsverse/transloco';

import {
  BookingDetailResponse,
  BookingService,
} from '../../../core/services/booking.service';
import { ToastService } from '../../../core/services/toast.service';
import { PLACEHOLDER_IMAGE } from '../../../shared/constants/images';

@Component({
  selector: 'app-booking-detail',
  standalone: true,
  imports: [CommonModule, RouterLink, TranslocoPipe],
  templateUrl: './booking-detail.component.html',
  styleUrl: './booking-detail.component.scss',
})
export class BookingDetailComponent implements OnInit {
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);
  private readonly bookingService = inject(BookingService);
  private readonly toast = inject(ToastService);
  private readonly t = inject(TranslocoService);

  booking: BookingDetailResponse | null = null;
  loading = true;
  cancelling = false;
  error: string | null = null;
  showCancelModal = false;

  readonly placeholderImage = PLACEHOLDER_IMAGE;

  ngOnInit(): void {
    this.route.paramMap.subscribe((params) => {
      const bookingId = params.get('id');
      if (!bookingId) {
        this.error = this.t.translate('bookingDetail.notFound');
        this.loading = false;
        return;
      }
      this.loadBooking(bookingId);
    });
  }

  get coverImage(): string {
    if (!this.booking) {
      return this.placeholderImage;
    }

    return this.booking.hotel.imagenes[0]
      || this.booking.habitacion.imagenes[0]
      || this.placeholderImage;
  }

  private getUtcDateOnlyTime(value: string): number {
    const [year, month, day] = value.split('-').map(Number);

    if (
      !Number.isInteger(year)
      || !Number.isInteger(month)
      || !Number.isInteger(day)
    ) {
      return Number.NaN;
    }

    return Date.UTC(year, month - 1, day);
  }

  get nights(): number {
    if (!this.booking) return 1;

    const startUtc = this.getUtcDateOnlyTime(this.booking.fecha_entrada);
    const endUtc = this.getUtcDateOnlyTime(this.booking.fecha_salida);
    const days = (endUtc - startUtc) / (1000 * 60 * 60 * 24);
    return Number.isFinite(days) && days > 0 ? days : 1;
  }

  get subtotal(): number {
    return (this.booking?.habitacion.monto ?? 0) * this.nights;
  }

  get taxes(): number {
    return this.booking?.habitacion.impuestos ?? 0;
  }

  get total(): number {
    return this.subtotal + this.taxes;
  }

  get statusClass(): string {
    const status = this.booking?.estado;
    if (status === 'confirmada') return 'booking-status--confirmed';
    if (status === 'pendiente') return 'booking-status--pending';
    if (status === 'cancelada') return 'booking-status--cancelled';
    return 'booking-status--completed';
  }

  get statusLabel(): string {
    const status = this.booking?.estado;
    if (status === 'confirmada') return this.t.translate('bookingDetail.statusConfirmed');
    if (status === 'pendiente') return this.t.translate('bookingDetail.statusPending');
    if (status === 'cancelada') return this.t.translate('bookingDetail.statusCancelled');
    return this.t.translate('bookingDetail.statusCompleted');
  }

  get canModify(): boolean {
    const status = this.booking?.estado;
    return !!this.booking?.hotel.id && (status === 'confirmada' || status === 'pendiente');
  }

  get canCancel(): boolean {
    const status = this.booking?.estado;
    return !this.cancelling && (status === 'confirmada' || status === 'pendiente');
  }

  formatDisplayDate(value: string): string {
    const date = this.parseDateOnly(value);
    return date.toLocaleDateString(this.localeCode, {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  }

  formatCurrency(value: number | null | undefined): string {
    return (value ?? 0).toLocaleString(this.localeCode);
  }

  formatHotelTime(value: string | null, fallback: string): string {
    if (!value) {
      return fallback;
    }
    const match = /^(\d{2}):(\d{2})/.exec(value);
    if (!match) {
      return fallback;
    }

    const hours = Number(match[1]);
    const minutes = Number(match[2]);
    const reference = new Date();
    reference.setHours(hours, minutes, 0, 0);

    return this.t.translate('bookingDetail.afterTime', {
      time: reference.toLocaleTimeString(this.localeCode, {
      hour: 'numeric',
      minute: '2-digit',
      hour12: true,
      }),
    });
  }

  get bookingLocation(): string {
    if (!this.booking) return this.t.translate('bookingDetail.unknownLocation');

    const city = this.booking.hotel.ciudad?.trim();
    const country = this.booking.hotel.pais?.trim();

    if (city && country) return `${city}, ${country}`;
    if (city) return city;
    if (country) return country;
    return this.t.translate('bookingDetail.unknownLocation');
  }

  get defaultCheckInHint(): string {
    return this.t.translate('bookingDetail.defaultCheckInHint');
  }

  get defaultCheckOutHint(): string {
    return this.t.translate('bookingDetail.defaultCheckOutHint');
  }

  onImageError(event: Event): void {
    const img = event.target as HTMLImageElement;
    img.src = this.placeholderImage;
  }

  onModifyReservation(): void {
    if (!this.booking) {
      return;
    }

    this.router.navigate(['/bookings', this.booking.id, 'edit']);
  }

  onCancelReservation(): void {
    if (!this.booking || !this.canCancel) {
      return;
    }
    this.showCancelModal = true;
  }

  closeCancelModal(): void {
    this.showCancelModal = false;
  }

  confirmCancel(): void {
    if (!this.booking) {
      return;
    }

    this.showCancelModal = false;
    this.cancelling = true;
    this.bookingService.cancelReservation(this.booking.id).subscribe({
      next: () => {
        this.toast.success(this.t.translate('bookingDetail.cancelSuccess'));
        this.cancelling = false;
        this.loadBooking(this.booking!.id);
      },
      error: () => {
        this.toast.danger(this.t.translate('bookingDetail.cancelError'));
        this.cancelling = false;
      },
    });
  }

  private loadBooking(bookingId: string): void {
    this.loading = true;
    this.error = null;
    this.booking = null;

    this.bookingService.getBookingById(bookingId).subscribe({
      next: (booking) => {
        this.booking = booking;
        this.loading = false;
      },
      error: (err: HttpErrorResponse) => {
        if (err.status === 404) {
          this.error = this.t.translate('bookingDetail.notFound');
        } else {
          this.error = this.t.translate('bookingDetail.loadError');
        }
        this.loading = false;
      },
    });
  }

  private parseDateOnly(value: string): Date {
    const match = /^(\d{4})-(\d{2})-(\d{2})$/.exec(value);
    if (!match) {
      return new Date(value);
    }

    return new Date(Number(match[1]), Number(match[2]) - 1, Number(match[3]));
  }

  private get localeCode(): string {
    return this.t.getActiveLang() === 'en' ? 'en-US' : 'es-CO';
  }
}