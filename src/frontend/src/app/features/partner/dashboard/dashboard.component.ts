import { CommonModule } from '@angular/common';
import { Component, OnInit, OnDestroy, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { TranslocoPipe, TranslocoService } from '@jsverse/transloco';

import {
  BookingService,
  BookingStatus,
  HotelBookingResponse,
  HotelReservationsFilters,
  PaymentStatus,
} from '../../../core/services/booking.service';
import type { HabitacionDetalle } from '../../../core/services/hotel.service';
import { ToastService } from '../../../core/services/toast.service';

type ReservationAction = 'confirm' | 'reject';

@Component({
  selector: 'app-partner-dashboard',
  standalone: true,
  imports: [CommonModule, FormsModule, TranslocoPipe],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.scss',
})
export class PartnerDashboardComponent implements OnInit, OnDestroy {
  reservations: HotelBookingResponse[] = [];
  habitaciones: HabitacionDetalle[] = [];
  totalReservations = 0;
  limit = 10;
  skip = 0;
  loading = false;
  loadError = false;
  refreshing = false;
  actionReservationId: string | null = null;
  actionType: ReservationAction | null = null;

  // Filter state
  searchGuest = '';
  selectedHabitacion: string | null = null;
  fechaInicio: string | null = null;
  fechaFin: string | null = null;
  selectedEstado: BookingStatus | null = null;
  selectedNumHuespedes: number | null = null;
  showMoreFilters = false;

  private readonly bookingService = inject(BookingService);
  private readonly toast = inject(ToastService);
  private readonly transloco = inject(TranslocoService);
  private searchDebounceTimer: ReturnType<typeof setTimeout> | null = null;

  ngOnInit(): void {
    this.loadReservations();
  }

  ngOnDestroy(): void {
    if (this.searchDebounceTimer) {
      clearTimeout(this.searchDebounceTimer);
    }
  }

  onSearchGuestChange(): void {
    if (this.searchDebounceTimer) {
      clearTimeout(this.searchDebounceTimer);
    }
    this.searchDebounceTimer = setTimeout(() => this.applyFilters(), 300);
  }

  onFilterChange(): void {
    this.applyFilters();
  }

  toggleMoreFilters(): void {
    this.showMoreFilters = !this.showMoreFilters;
  }

  clearFilters(): void {
    this.searchGuest = '';
    this.selectedHabitacion = null;
    this.fechaInicio = null;
    this.fechaFin = null;
    this.selectedEstado = null;
    this.selectedNumHuespedes = null;
    this.showMoreFilters = false;
    this.applyFilters();
  }

  hasActiveFilters(): boolean {
    return !!(
      this.searchGuest ||
      this.selectedHabitacion ||
      this.fechaInicio ||
      this.fechaFin ||
      this.selectedEstado ||
      this.selectedNumHuespedes !== null
    );
  }

  private applyFilters(): void {
    this.skip = 0;
    this.loadReservations();
  }
  get currentPage(): number {
    return Math.floor(this.skip / this.limit) + 1;
  }

  get totalPages(): number {
    return this.totalReservations === 0 ? 1 : Math.ceil(this.totalReservations / this.limit);
  }

  get hasPreviousPage(): boolean {
    return this.skip > 0;
  }

  get hasNextPage(): boolean {
    return this.skip + this.limit < this.totalReservations;
  }

  refreshReservations(): void {
    if (this.loading || this.refreshing) {
      return;
    }
    this.loadReservations(true);
  }

  previousPage(): void {
    if (!this.hasPreviousPage || this.loading || this.refreshing) {
      return;
    }
    this.skip = Math.max(this.skip - this.limit, 0);
    this.loadReservations();
  }

  nextPage(): void {
    if (!this.hasNextPage || this.loading || this.refreshing) {
      return;
    }
    this.skip += this.limit;
    this.loadReservations();
  }

  confirmReservation(reservation: HotelBookingResponse): void {
    if (!this.canConfirm(reservation) || this.actionReservationId !== null) {
      return;
    }

    this.actionReservationId = reservation.id;
    this.actionType = 'confirm';
    this.bookingService.confirmHotelReservation(reservation.id).subscribe({
      next: () => {
        this.toast.success(
          this.transloco.translate('partner.dashboard.reservations.toastConfirmSuccess')
        );
        this.clearActionState();
        this.loadReservations();
      },
      error: () => {
        this.toast.danger(
          this.transloco.translate('partner.dashboard.reservations.toastConfirmError')
        );
        this.clearActionState();
      },
    });
  }

  rejectReservation(reservation: HotelBookingResponse): void {
    if (!this.canReject(reservation) || this.actionReservationId !== null) {
      return;
    }

    this.actionReservationId = reservation.id;
    this.actionType = 'reject';
    this.bookingService.rejectHotelReservation(reservation.id).subscribe({
      next: () => {
        this.toast.success(
          this.transloco.translate('partner.dashboard.reservations.toastRejectSuccess')
        );
        this.clearActionState();
        this.loadReservations();
      },
      error: () => {
        this.toast.danger(
          this.transloco.translate('partner.dashboard.reservations.toastRejectError')
        );
        this.clearActionState();
      },
    });
  }

  canConfirm(reservation: HotelBookingResponse): boolean {
    return reservation.estado === 'pendiente';
  }

  canReject(reservation: HotelBookingResponse): boolean {
    return reservation.estado === 'pendiente' || reservation.estado === 'confirmada';
  }

  isProcessing(reservationId: string, action?: ReservationAction): boolean {
    return this.actionReservationId === reservationId && (!action || this.actionType === action);
  }

  trackByReservationId(_: number, reservation: HotelBookingResponse): string {
    return reservation.id;
  }

  getAvatarInitials(name: string | null): string {
    if (!name) {
      return 'NA';
    }

    const parts = name.trim().split(/\s+/).slice(0, 2);
    return parts.map((part) => part.charAt(0).toUpperCase()).join('');
  }

  getAvatarClass(index: number): string {
    const classes = ['avatar-yellow', 'avatar-blue', 'avatar-purple'];
    return classes[index % classes.length];
  }

  getGuestLine(reservation: HotelBookingResponse): string {
    const roomLabel =
      reservation.nombre_habitacion ||
      reservation.numero_habitacion ||
      this.transloco.translate('partner.dashboard.reservations.noRoom');
    return `${roomLabel} • ${this.formatGuestCount(reservation.num_huespedes)}`;
  }

  formatDateRange(startDate: string, endDate: string): string {
    const locale = this.getLocale();
    const start = this.toLocalDate(startDate);
    const end = this.toLocalDate(endDate);
    const startFormatter = new Intl.DateTimeFormat(locale, {
      month: 'short',
      day: '2-digit',
    });
    const endFormatter = new Intl.DateTimeFormat(locale, {
      month: 'short',
      day: '2-digit',
      year: 'numeric',
    });

    return `${startFormatter.format(start)} - ${endFormatter.format(end)}`;
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

  formatAmount(amount: number | null): string {
    const safeAmount = amount ?? 0;
    const formatted = new Intl.NumberFormat(this.getLocale(), {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(safeAmount);
    return `$${formatted}`;
  }

  getPaymentStatusLabel(status: PaymentStatus | null): string {
    if (status === 'successful') {
      return this.transloco.translate('partner.dashboard.reservations.paymentPaid');
    }
    if (status === 'failed') {
      return this.transloco.translate('partner.dashboard.reservations.paymentFailed');
    }
    return this.transloco.translate('partner.dashboard.reservations.paymentPending');
  }

  getPaymentStatusClass(status: PaymentStatus | null): string {
    if (status === 'successful') {
      return 'status-prepaid';
    }
    if (status === 'failed') {
      return 'status-failed';
    }
    return 'status-pending';
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

  private loadReservations(isRefresh = false): void {
    this.loading = !isRefresh;
    this.refreshing = isRefresh;
    this.loadError = false;

    const filters: HotelReservationsFilters = {};
    const validNumHuespedes =
      this.selectedNumHuespedes !== null &&
      Number.isInteger(this.selectedNumHuespedes) &&
      this.selectedNumHuespedes >= 1
        ? this.selectedNumHuespedes
        : null;

    if (this.searchGuest.trim()) filters.nombre_viajero = this.searchGuest.trim();
    if (this.selectedHabitacion) filters.tipo_habitacion = this.selectedHabitacion;
    if (this.selectedEstado) filters.estado = this.selectedEstado;
    if (this.fechaInicio) filters.fecha_inicio = this.fechaInicio;
    if (this.fechaFin) filters.fecha_fin = this.fechaFin;
    if (validNumHuespedes !== null) filters.num_huespedes = validNumHuespedes;

    this.bookingService.getHotelReservations(this.skip, this.limit, filters).subscribe({
      next: (response) => {
        this.reservations = response.reservas;
        this.totalReservations = response.total;
        this.habitaciones = response.habitaciones;
        this.loading = false;
        this.refreshing = false;
      },
      error: () => {
        this.loading = false;
        this.refreshing = false;
        this.loadError = true;
        this.toast.danger(
          this.transloco.translate('partner.dashboard.reservations.loadError')
        );
      },
    });
  }

  private clearActionState(): void {
    this.actionReservationId = null;
    this.actionType = null;
  }

  private getLocale(): string {
    return this.transloco.getActiveLang() === 'es' ? 'es-CO' : 'en-US';
  }

  private toLocalDate(value: string): Date {
    const [year, month, day] = value.split('-').map(Number);
    return new Date(year, month - 1, day);
  }
}
