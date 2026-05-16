import { CommonModule } from '@angular/common';
import { Component, OnInit, OnDestroy, DestroyRef, inject, ViewChild, ElementRef, AfterViewInit } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { FormsModule } from '@angular/forms';
import { TranslocoPipe, TranslocoService } from '@jsverse/transloco';
import { Subject, switchMap, EMPTY, catchError } from 'rxjs';
import { generateRevenuePdf } from './generate-revenue-pdf';
import {
  Chart,
  BarController,
  BarElement,
  CategoryScale,
  LinearScale,
  Tooltip,
} from 'chart.js';

Chart.register(BarController, BarElement, CategoryScale, LinearScale, Tooltip);

import {
  BookingService,
  BookingStatus,
  HotelBookingResponse,
  HotelReservationsFilters,
  PaymentStatus,
  ReporteIngresosResponse,
} from '../../../core/services/booking.service';
import { ReservationDetailModalComponent } from '../components/reservation-detail-modal/reservation-detail-modal.component';
import type { HabitacionDetalle } from '../../../core/services/hotel.service';
import { ToastService } from '../../../core/services/toast.service';

type ReservationAction = 'confirm' | 'reject';

interface LoadReservationsParams {
  skip: number;
  limit: number;
  filters: HotelReservationsFilters;
  isRefresh: boolean;
}

@Component({
  selector: 'app-partner-dashboard',
  standalone: true,
  imports: [CommonModule, FormsModule, TranslocoPipe, ReservationDetailModalComponent],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.scss',
})
export class PartnerDashboardComponent implements OnInit, OnDestroy, AfterViewInit {
  @ViewChild('revenueChart') revenueChartRef!: ElementRef<HTMLCanvasElement>;
  reservations: HotelBookingResponse[] = [];
  habitaciones: HabitacionDetalle[] = [];
  totalReservations = 0;
  limit = 10;
  skip = 0;
  loading = false;
  loadError = false;
  refreshing = false;
  selectedReservation: HotelBookingResponse | null = null;
  actionReservationId: string | null = null;
  actionType: ReservationAction | null = null;

  isDownloadingReport = false;
  revenueReport: ReporteIngresosResponse | null = null;
  private revenueChartInstance: Chart | null = null;

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
  private readonly destroyRef = inject(DestroyRef);
  private searchDebounceTimer: ReturnType<typeof setTimeout> | null = null;

  private readonly loadTrigger$ = new Subject<LoadReservationsParams>();

  constructor() {
    this.loadTrigger$
      .pipe(
        switchMap((params) => {
          this.loading = !params.isRefresh;
          this.refreshing = params.isRefresh;
          this.loadError = false;
          return this.bookingService
            .getHotelReservations(params.skip, params.limit, params.filters)
            .pipe(
              catchError(() => {
                this.clearLoadingState();
                this.loadError = true;
                this.toast.danger(
                  this.transloco.translate('partner.dashboard.reservations.loadError')
                );
                return EMPTY;
              })
            );
        }),
        takeUntilDestroyed(this.destroyRef)
      )
      .subscribe((response) => {
        this.reservations = response.reservas;
        this.totalReservations = response.total;
        this.habitaciones = response.habitaciones;
        this.clearLoadingState();
      });
  }

  get currentMonthRevenue(): number {
    if (!this.revenueReport) return 0;
    const now = new Date();
    const entry = this.revenueReport.ingresos_por_mes.find(
      (m) => m.anio === now.getFullYear() && m.mes === now.getMonth() + 1
    );
    return entry?.ingresos_totales ?? 0;
  }

  ngOnInit(): void {
    this.loadReservations();
    this.loadRevenueReport();

    this.transloco.langChanges$
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe(() => this.renderRevenueChart());
  }

  ngAfterViewInit(): void {
    if (this.revenueReport) {
      this.renderRevenueChart();
    }
  }

  ngOnDestroy(): void {
    if (this.searchDebounceTimer) {
      clearTimeout(this.searchDebounceTimer);
    }
    this.revenueChartInstance?.destroy();
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
      this.searchGuest.trim() ||
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

  openReservationDetail(reservation: HotelBookingResponse): void {
    if (this.actionReservationId !== null) {
      return;
    }

    this.selectedReservation = reservation;
  }

  closeReservationDetail(): void {
    this.selectedReservation = null;
  }

  onReservationRowKeydown(event: KeyboardEvent, reservation: HotelBookingResponse): void {
    if (event.key !== 'Enter' && event.key !== ' ') {
      return;
    }

    if (event.target !== event.currentTarget) {
      return;
    }

    event.preventDefault();
    this.openReservationDetail(reservation);
  }

  confirmReservation(reservation: HotelBookingResponse, event?: Event): void {
    event?.stopPropagation();
    this.executeReservationAction(reservation, 'confirm');
  }

  rejectReservation(reservation: HotelBookingResponse, event?: Event): void {
    event?.stopPropagation();
    this.executeReservationAction(reservation, 'reject');
  }

  confirmSelectedReservation(): void {
    if (!this.selectedReservation) {
      return;
    }

    this.executeReservationAction(this.selectedReservation, 'confirm', true);
  }

  rejectSelectedReservation(): void {
    if (!this.selectedReservation) {
      return;
    }

    this.executeReservationAction(this.selectedReservation, 'reject', true);
  }

  private executeReservationAction(
    reservation: HotelBookingResponse,
    action: ReservationAction,
    closeDetailOnSuccess = false,
  ): void {
    const canPerform = action === 'confirm'
      ? this.canConfirm(reservation)
      : this.canReject(reservation);

    if (!canPerform || this.actionReservationId !== null) {
      return;
    }

    this.actionReservationId = reservation.id;
    this.actionType = action;

    const request$ = action === 'confirm'
      ? this.bookingService.confirmHotelReservation(reservation.id)
      : this.bookingService.rejectHotelReservation(reservation.id);
    const successKey = action === 'confirm'
      ? 'partner.dashboard.reservations.toastConfirmSuccess'
      : 'partner.dashboard.reservations.toastRejectSuccess';
    const errorKey = action === 'confirm'
      ? 'partner.dashboard.reservations.toastConfirmError'
      : 'partner.dashboard.reservations.toastRejectError';

    request$.subscribe({
      next: () => {
        this.toast.success(this.transloco.translate(successKey));
        this.clearActionState();
        if (closeDetailOnSuccess) {
          this.closeReservationDetail();
        }
        this.loadReservations();
      },
      error: () => {
        this.toast.danger(this.transloco.translate(errorKey));
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

  private loadRevenueReport(): void {
    this.bookingService.getHotelRevenueReport().subscribe({
      next: (data) => {
        this.revenueReport = data;
        this.renderRevenueChart();
      },
      error: () => {
        // Degrade gracefully — chart stays empty, total shows $0
      },
    });
  }

  private renderRevenueChart(): void {
    if (!this.revenueChartRef?.nativeElement) {
      return;
    }

    const lang = this.transloco.getActiveLang();
    const isEs = lang === 'es';
    const monthNames = isEs
      ? ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic']
      : ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];

    const currentYear = new Date().getFullYear();
    const currentMonth = new Date().getMonth() + 1; // 1-based

    // Build a lookup from existing data: key = "year-month"
    const dataByMonth = new Map<string, number>();
    for (const entry of (this.revenueReport?.ingresos_por_mes ?? [])) {
      dataByMonth.set(`${entry.anio}-${entry.mes}`, entry.ingresos_totales);
    }

    // All 12 months of the current year, up to today
    const labels: string[] = [];
    const values: number[] = [];
    for (let m = 1; m <= 12; m++) {
      labels.push(monthNames[m - 1]);
      const amount = dataByMonth.get(`${currentYear}-${m}`) ?? 0;
      values.push(amount);
    }

    this.revenueChartInstance?.destroy();
    this.revenueChartInstance = new Chart(this.revenueChartRef.nativeElement, {
      type: 'bar',
      data: {
        labels,
        datasets: [
          {
            data: values,
            backgroundColor: (ctx) => {
              const isCurrent = ctx.dataIndex === currentMonth - 1;
              return isCurrent ? 'rgb(30, 80, 180)' : 'rgba(30, 80, 180, 0.25)';
            },
            borderRadius: 3,
            borderSkipped: false,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        animation: { duration: 600 },
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: (ctx) => {
                const val = ctx.parsed.y as number;
                return ' ' + this.formatAmount(val);
              },
              title: (items) => items[0].label,
            },
          },
        },
        scales: {
          x: {
            grid: { display: false },
            border: { display: false },
            ticks: {
              font: { size: 9 },
              color: '#9ca3af',
              maxRotation: 0,
            },
          },
          y: {
            display: false,
            beginAtZero: true,
          },
        },
      },
    });
  }

  downloadReport(): void {
    if (this.isDownloadingReport) {
      return;
    }
    this.isDownloadingReport = true;
    this.bookingService.getHotelRevenueReport().subscribe({
      next: (data) => {
        this.generatePdf(data);
        this.isDownloadingReport = false;
      },
      error: () => {
        this.toast.danger(
          this.transloco.translate('partner.dashboard.stats.downloadError')
        );
        this.isDownloadingReport = false;
      },
    });
  }

  private generatePdf(data: ReporteIngresosResponse): void {
    generateRevenuePdf(data, this.transloco.getActiveLang());
  }

  private loadReservations(isRefresh = false): void {
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

    this.loadTrigger$.next({ skip: this.skip, limit: this.limit, filters, isRefresh });
  }

  private clearActionState(): void {
    this.actionReservationId = null;
    this.actionType = null;
  }

  private clearLoadingState(): void {
    this.loading = false;
    this.refreshing = false;
  }

  private getLocale(): string {
    return this.transloco.getActiveLang() === 'es' ? 'es-CO' : 'en-US';
  }

  private toLocalDate(value: string): Date {
    const [year, month, day] = value.split('-').map(Number);
    return new Date(year, month - 1, day);
  }
}
