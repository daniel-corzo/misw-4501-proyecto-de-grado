import { CommonModule } from '@angular/common';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { Component, DestroyRef, effect, inject, input, output } from '@angular/core';
import { TranslocoPipe, TranslocoService } from '@jsverse/transloco';
import { EMPTY, Subject, catchError, from, map, of, switchMap } from 'rxjs';
import * as QRCode from 'qrcode';

import {
  BookingStatus,
  BookingService,
  HotelBookingDetailResponse,
  PaymentStatusFilter,
} from '../../../../core/services/booking.service';
import { ModalComponent } from '../../../../shared/components/modal/modal.component';
import { PLACEHOLDER_IMAGE } from '../../../../shared/constants/images';

type ReservationAction = 'confirm' | 'reject';

@Component({
  selector: 'app-reservation-detail-modal',
  standalone: true,
  imports: [CommonModule, ModalComponent, TranslocoPipe],
  templateUrl: './reservation-detail-modal.component.html',
  styleUrl: './reservation-detail-modal.component.scss',
})
export class ReservationDetailModalComponent {
  reservationId = input.required<string>();
  actionsLocked = input(false);
  processingAction = input<ReservationAction | null>(null);

  closed = output<void>();
  confirmRequested = output<void>();
  rejectRequested = output<void>();

  detail: HotelBookingDetailResponse | null = null;
  qrDataUrl: string | null = null;
  loading = false;
  loadError = false;

  readonly placeholderImage = PLACEHOLDER_IMAGE;

  private readonly bookingService = inject(BookingService);
  private readonly transloco = inject(TranslocoService);
  private readonly destroyRef = inject(DestroyRef);
  private readonly detailTrigger$ = new Subject<string>();

  constructor() {
    this.detailTrigger$
      .pipe(
        switchMap((reservationId) => {
          this.loading = true;
          this.loadError = false;
          this.detail = null;
          this.qrDataUrl = null;

          return this.bookingService.getHotelBookingById(reservationId).pipe(
            switchMap((detail) =>
              from(
                QRCode.toDataURL(detail.qr_checkin_payload, {
                  margin: 1,
                  width: 192,
                  color: {
                    dark: '#0f172a',
                    light: '#0000',
                  },
                })
              ).pipe(
                map((qrDataUrl) => ({
                  detail,
                  qrDataUrl,
                })),
                catchError(() => of({ detail, qrDataUrl: null }))
              )
            ),
            catchError(() => {
              this.loading = false;
              this.loadError = true;
              return EMPTY;
            })
          );
        }),
        takeUntilDestroyed(this.destroyRef)
      )
      .subscribe(({ detail, qrDataUrl }) => {
        this.detail = detail;
        this.qrDataUrl = qrDataUrl;
        this.loading = false;
      });

    effect(() => {
      const reservationId = this.reservationId();
      if (reservationId) {
        this.detailTrigger$.next(reservationId);
      }
    });
  }

  get modalTitle(): string {
    return this.transloco.translate('partner.dashboard.reservations.detailTitle');
  }

  get coverImage(): string {
    if (!this.detail) {
      return this.placeholderImage;
    }

    return (
      this.detail.hotel.imagenes[0]
      || this.detail.habitacion.imagenes[0]
      || this.placeholderImage
    );
  }

  get hotelLocation(): string {
    if (!this.detail) {
      return this.transloco.translate('partner.dashboard.reservations.detailLocationFallback');
    }

    const city = this.detail.hotel.ciudad?.trim();
    const country = this.detail.hotel.pais?.trim();

    if (city && country) {
      return `${city}, ${country}`;
    }
    if (city) {
      return city;
    }
    if (country) {
      return country;
    }
    return this.transloco.translate('partner.dashboard.reservations.detailLocationFallback');
  }

  reloadDetail(): void {
    const reservationId = this.reservationId();
    if (reservationId) {
      this.detailTrigger$.next(reservationId);
    }
  }

  canConfirm(): boolean {
    return this.detail?.estado === 'pendiente';
  }

  canReject(): boolean {
    return this.detail?.estado === 'pendiente' || this.detail?.estado === 'confirmada';
  }

  requestConfirm(): void {
    if (!this.canConfirm() || this.actionsLocked()) {
      return;
    }

    this.confirmRequested.emit();
  }

  requestReject(): void {
    if (!this.canReject() || this.actionsLocked()) {
      return;
    }

    this.rejectRequested.emit();
  }

  isProcessing(action: ReservationAction): boolean {
    return this.processingAction() === action;
  }

  formatDisplayDate(value: string): string {
    const date = this.parseDateOnly(value);
    return date.toLocaleDateString(this.localeCode, {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  }

  formatDateTime(value: string | null): string {
    if (!value) {
      return this.transloco.translate('partner.dashboard.reservations.detailNotAvailable');
    }

    const date = new Date(value);
    if (Number.isNaN(date.getTime())) {
      return this.transloco.translate('partner.dashboard.reservations.detailNotAvailable');
    }

    return date.toLocaleString(this.localeCode, {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
    });
  }

  formatHotelTime(value: string | null, fallbackKey: string): string {
    if (!value) {
      return this.transloco.translate(fallbackKey);
    }

    const match = /^(\d{2}):(\d{2})/.exec(value);
    if (!match) {
      return this.transloco.translate(fallbackKey);
    }

    const reference = new Date();
    reference.setHours(Number(match[1]), Number(match[2]), 0, 0);
    return this.transloco.translate('bookingDetail.afterTime', {
      time: reference.toLocaleTimeString(this.localeCode, {
        hour: 'numeric',
        minute: '2-digit',
        hour12: true,
      }),
    });
  }

  formatAmount(value: number | null): string {
    if (value === null) {
      return this.transloco.translate('partner.dashboard.reservations.detailNotAvailable');
    }

    const formatted = new Intl.NumberFormat(this.localeCode, {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(value);
    return `$${formatted}`;
  }

  formatNightCount(totalNights: number): string {
    const key =
      totalNights === 1
        ? 'partner.dashboard.reservations.nightSingular'
        : 'partner.dashboard.reservations.nightPlural';
    return this.transloco.translate(key, { count: totalNights });
  }

  formatGuestCount(totalGuests: number): string {
    const key =
      totalGuests === 1
        ? 'partner.dashboard.reservations.guestSingular'
        : 'partner.dashboard.reservations.guestPlural';
    return this.transloco.translate(key, { count: totalGuests });
  }

  formatAmenityLabel(amenity: string): string {
    return amenity
      .toLowerCase()
      .split('_')
      .filter(Boolean)
      .map((segment) => segment.charAt(0).toUpperCase() + segment.slice(1))
      .join(' ');
  }

  getReservationStatusLabel(status: BookingStatus): string {
    switch (status) {
      case 'confirmada':
        return this.transloco.translate('bookings.statusConfirmed');
      case 'cancelada':
        return this.transloco.translate('bookings.statusCancelled');
      case 'completada':
        return this.transloco.translate('bookings.statusCompleted');
      default:
        return this.transloco.translate('bookings.statusPending');
    }
  }

  getReservationStatusClass(status: BookingStatus): string {
    return `is-${status}`;
  }

  getPaymentStatusLabel(status: PaymentStatusFilter): string {
    if (status === 'successful') {
      return this.transloco.translate('partner.dashboard.reservations.paymentPaid');
    }
    if (status === 'failed') {
      return this.transloco.translate('partner.dashboard.reservations.paymentFailed');
    }
    return this.transloco.translate('partner.dashboard.reservations.paymentPending');
  }

  getPaymentStatusClass(status: PaymentStatusFilter): string {
    return `is-${status}`;
  }

  onImageError(event: Event): void {
    const image = event.target as HTMLImageElement;
    image.src = this.placeholderImage;
  }

  private parseDateOnly(value: string): Date {
    const [year, month, day] = value.split('-').map(Number);
    return new Date(year, month - 1, day);
  }

  private get localeCode(): string {
    return this.transloco.getActiveLang() === 'en' ? 'en-US' : 'es-CO';
  }
}
