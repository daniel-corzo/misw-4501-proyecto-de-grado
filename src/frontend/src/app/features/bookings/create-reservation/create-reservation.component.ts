import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpErrorResponse } from '@angular/common/http';
import { Component, OnInit, inject } from '@angular/core';
import { ActivatedRoute, ParamMap, Router, RouterLink } from '@angular/router';
import { TranslocoPipe, TranslocoService } from '@jsverse/transloco';
import { EMPTY } from 'rxjs';
import { catchError, map, switchMap } from 'rxjs/operators';

import {
  BookingDetailResponse,
  BookingService,
  UpdateBookingRequest,
} from '../../../core/services/booking.service';
import {
  HabitacionDetalle,
  HotelDetalle,
  HotelService,
} from '../../../core/services/hotel.service';
import { ToastService } from '../../../core/services/toast.service';
import { PLACEHOLDER_IMAGE } from '../../../shared/constants/images';

type ReservationFormMode = 'create' | 'edit';

interface InitialSnapshot {
  habitacionId: string;
  fechaEntrada: string;
  fechaSalida: string;
  numHuespedes: number;
}

@Component({
  selector: 'app-create-reservation',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink, TranslocoPipe],
  templateUrl: './create-reservation.component.html',
  styleUrl: './create-reservation.component.scss',
})
export class CreateReservationComponent implements OnInit {
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);
  private readonly hotelService = inject(HotelService);
  private readonly bookingService = inject(BookingService);
  private readonly toast = inject(ToastService);
  private readonly t = inject(TranslocoService);

  mode: ReservationFormMode = 'create';
  hotel: HotelDetalle | null = null;
  selectedRoom: HabitacionDetalle | null = null;
  /** Present only in edit mode */
  existingBooking: BookingDetailResponse | null = null;
  reservaId: string | null = null;
  /** Initial snapshot for edit mode; exposed for template (room “current” label). */
  initial: InitialSnapshot | null = null;

  loading = true;
  submitting = false;
  error: string | null = null;

  fechaEntrada: string | null = null;
  fechaSalida: string | null = null;
  numHuespedes = 1;

  readonly placeholderImage = PLACEHOLDER_IMAGE;

  ngOnInit(): void {
    this.route.paramMap
      .pipe(
        switchMap((params: ParamMap) => {
          const mode = (this.route.snapshot.data['reservationFormMode'] ??
            'create') as ReservationFormMode;
          this.mode = mode;
          this.resetState();
          this.loading = true;
          this.error = null;

          if (mode === 'create') {
            const hotelId = params.get('id');
            if (!hotelId) {
              this.setLoadError('createReservation.hotelNotFound');
              this.loading = false;
              return EMPTY;
            }
            return this.hotelService.getHotelById(hotelId).pipe(
              catchError(() => {
                this.setLoadError('createReservation.loadError');
                this.loading = false;
                return EMPTY;
              })
            );
          }

          const bookingId = params.get('id');
          if (!bookingId) {
            this.setLoadError('createReservation.bookingNotFound');
            this.loading = false;
            return EMPTY;
          }
          this.reservaId = bookingId;

          return this.bookingService.getBookingById(bookingId).pipe(
            switchMap((booking) => {
              this.existingBooking = booking;
              const hotelId = booking.hotel.id;
              if (!hotelId) {
                this.setLoadError('createReservation.hotelNotLinked');
                this.loading = false;
                return EMPTY;
              }
              return this.hotelService.getHotelById(hotelId).pipe(
                map((hotel) => ({ booking, hotel })),
                catchError(() => {
                  this.setLoadError('createReservation.loadError');
                  this.loading = false;
                  return EMPTY;
                })
              );
            }),
            catchError((err: HttpErrorResponse) => {
              this.loading = false;
              if (err.status === 404) {
                this.setLoadError('createReservation.bookingNotFound');
              } else {
                this.setLoadError('createReservation.loadError');
              }
              return EMPTY;
            })
          );
        })
      )
      .subscribe({
        next: (result: HotelDetalle | { booking: BookingDetailResponse; hotel: HotelDetalle }) => {
          if (this.mode === 'create') {
            this.applyCreateLoad(result as HotelDetalle);
            return;
          }
          const { booking, hotel } = result as {
            booking: BookingDetailResponse;
            hotel: HotelDetalle;
          };
          this.applyEditAfterHotelLoad(booking, hotel);
        },
      });
  }

  private setLoadError(key: string): void {
    this.error = this.t.translate(key);
  }

  private resetState(): void {
    this.hotel = null;
    this.selectedRoom = null;
    this.existingBooking = null;
    this.reservaId = null;
    this.initial = null;
    this.fechaEntrada = null;
    this.fechaSalida = null;
    this.numHuespedes = 1;
  }

  private applyCreateLoad(hotel: HotelDetalle): void {
    this.hotel = hotel;
    const q = this.route.snapshot.queryParamMap;
    const { entrada, salida } = this.stayDatesFromCreateQuery(q);
    const guests = Number(q.get('huespedes') ?? '1') || 1;

    this.fechaEntrada = entrada;
    this.fechaSalida = salida;
    this.clampNumHuespedesForRoom(null);
    this.numHuespedes = Math.min(Math.max(1, guests), this.maxGuestLimit(null));

    if (hotel.habitaciones.length > 0) {
      this.selectedRoom =
        hotel.habitaciones.find((h) => h.disponible) ?? hotel.habitaciones[0];
      this.clampNumHuespedesForRoom(this.selectedRoom);
    }
    this.loading = false;
  }

  private applyEditAfterHotelLoad(
    booking: BookingDetailResponse,
    hotel: HotelDetalle
  ): void {
    this.hotel = hotel;
    this.fechaEntrada = booking.fecha_entrada;
    this.fechaSalida = booking.fecha_salida;
    this.numHuespedes = booking.num_huespedes;
    this.selectedRoom =
      hotel.habitaciones.find((h) => h.id === booking.habitacion.id) ?? null;
    if (!this.selectedRoom && hotel.habitaciones.length > 0) {
      this.selectedRoom =
        hotel.habitaciones.find((h) => h.disponible) ?? hotel.habitaciones[0];
    }
    this.clampNumHuespedesForRoom(this.selectedRoom);
    this.initial = {
      habitacionId: booking.habitacion.id,
      fechaEntrada: booking.fecha_entrada,
      fechaSalida: booking.fecha_salida,
      numHuespedes: booking.num_huespedes,
    };
    this.loading = false;
  }

  private defaultDatePlusDays(offset: number): string {
    const d = new Date();
    d.setDate(d.getDate() + offset);
    return this.toYmd(d);
  }

  private toYmd(d: Date): string {
    const y = d.getFullYear();
    const m = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    return `${y}-${m}-${day}`;
  }

  private readonly ymdPattern = /^\d{4}-\d{2}-\d{2}$/;

  /** Validates `YYYY-MM-DD` shape and that the triplet is a real calendar date (UTC). */
  private isValidYmd(s: string | null | undefined): boolean {
    if (s == null || !this.ymdPattern.test(s)) {
      return false;
    }
    const [y, mo, d] = s.split('-').map(Number);
    if (![y, mo, d].every((n) => Number.isInteger(n))) {
      return false;
    }
    const dt = new Date(Date.UTC(y, mo - 1, d));
    return (
      dt.getUTCFullYear() === y &&
      dt.getUTCMonth() === mo - 1 &&
      dt.getUTCDate() === d
    );
  }

  /**
   * Uses query `checkIn` / `checkOut` only when both match `YYYY-MM-DD`, represent real dates,
   * and check-out is strictly after check-in. Otherwise uses default stay (tomorrow → day after).
   */
  private stayDatesFromCreateQuery(q: ParamMap): { entrada: string; salida: string } {
    const defIn = this.defaultDatePlusDays(1);
    const defOut = this.defaultDatePlusDays(2);
    const inQ = q.get('checkIn');
    const outQ = q.get('checkOut');
    if (!this.isValidYmd(inQ) || !this.isValidYmd(outQ)) {
      return { entrada: defIn, salida: defOut };
    }
    if (outQ! <= inQ!) {
      return { entrada: defIn, salida: defOut };
    }
    return { entrada: inQ!, salida: outQ! };
  }

  private clampNumHuespedesForRoom(room: HabitacionDetalle | null): void {
    const cap = this.maxGuestLimit(room);
    if (this.numHuespedes > cap) {
      this.numHuespedes = cap;
    }
    if (this.numHuespedes < 1) {
      this.numHuespedes = 1;
    }
  }

  private maxGuestLimit(room: HabitacionDetalle | null): number {
    const c = room?.capacidad ?? 1;
    return Math.max(1, c);
  }

  get maxGuests(): number {
    return this.maxGuestLimit(this.selectedRoom);
  }

  /** Guest options 1..maxGuests */
  get guestOptions(): number[] {
    return Array.from({ length: this.maxGuests }, (_, i) => i + 1);
  }

  get minCheckOutYmd(): string {
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    if (!this.fechaEntrada || !this.isValidYmd(this.fechaEntrada)) {
      return this.toYmd(tomorrow);
    }
    const [y, m, d] = this.fechaEntrada.split('-').map(Number);
    const t = new Date(y, m - 1, d);
    t.setDate(t.getDate() + 1);
    return this.toYmd(t);
  }

  get minCheckInYmd(): string {
    return this.toYmd(new Date());
  }

  onCheckInChange(): void {
    if (
      this.fechaEntrada &&
      this.fechaSalida &&
      this.fechaSalida <= this.fechaEntrada
    ) {
      const [y, m, d] = this.fechaEntrada.split('-').map(Number);
      const t = new Date(y, m - 1, d);
      t.setDate(t.getDate() + 1);
      this.fechaSalida = this.toYmd(t);
    }
  }

  get wasModified(): boolean {
    if (this.mode !== 'edit' || !this.initial || !this.selectedRoom) {
      return true;
    }
    return (
      this.selectedRoom.id !== this.initial.habitacionId ||
      this.fechaEntrada !== this.initial.fechaEntrada ||
      this.fechaSalida !== this.initial.fechaSalida ||
      this.numHuespedes !== this.initial.numHuespedes
    );
  }

  get datesValid(): boolean {
    if (!this.fechaEntrada || !this.fechaSalida) {
      return false;
    }
    return this.fechaSalida > this.fechaEntrada;
  }

  get puedeEnviar(): boolean {
    if (this.submitting || !this.selectedRoom) {
      return false;
    }
    if (this.mode === 'create' && !this.selectedRoom.disponible) {
      return false;
    }
    if (
      this.mode === 'edit' &&
      !this.selectedRoom.disponible &&
      this.selectedRoom.id !== this.initial?.habitacionId
    ) {
      return false;
    }
    if (!this.datesValid) {
      return false;
    }
    if (this.mode === 'edit') {
      return this.wasModified;
    }
    return true;
  }

  get stayNights(): number {
    if (!this.fechaEntrada || !this.fechaSalida) {
      return 1;
    }
    const m1 = /^(\d{4})-(\d{2})-(\d{2})$/.exec(this.fechaEntrada);
    const m2 = /^(\d{4})-(\d{2})-(\d{2})$/.exec(this.fechaSalida);
    if (!m1 || !m2) {
      return 1;
    }
    const t1 = Date.UTC(+m1[1], +m1[2] - 1, +m1[3]);
    const t2 = Date.UTC(+m2[1], +m2[2] - 1, +m2[3]);
    const n = Math.round((t2 - t1) / (1000 * 60 * 60 * 24));
    return n > 0 ? n : 1;
  }

  get roomSubtotal(): number {
    return (this.selectedRoom?.monto ?? 0) * this.stayNights;
  }

  get roomTaxes(): number {
    return this.selectedRoom?.impuestos ?? 0;
  }

  get totalPrice(): number {
    return this.roomSubtotal + this.roomTaxes;
  }

  formatPrice(amount: number): string {
    return amount.toLocaleString(this.t.getActiveLang() === 'en' ? 'en-US' : 'es-CO');
  }

  selectRoom(room: HabitacionDetalle): void {
    if (this.mode === 'create' && !room.disponible) {
      return;
    }
    if (
      this.mode === 'edit' &&
      !room.disponible &&
      room.id !== this.initial?.habitacionId
    ) {
      return;
    }
    this.selectedRoom = room;
    this.clampNumHuespedesForRoom(room);
  }

  onNumHuespedesSelect(value: number | string): void {
    const n =
      typeof value === 'number' ? value : parseInt(String(value), 10);
    this.numHuespedes = Number.isFinite(n)
      ? Math.min(Math.max(1, n), this.maxGuests)
      : 1;
  }

  isRoomSelectable(room: HabitacionDetalle): boolean {
    if (this.mode === 'create') {
      return room.disponible;
    }
    return room.disponible || room.id === this.initial?.habitacionId;
  }

  onSubmit(): void {
    if (!this.puedeEnviar || !this.selectedRoom || !this.hotel) {
      return;
    }
    if (!this.fechaEntrada || !this.fechaSalida) {
      return;
    }

    if (this.mode === 'create') {
      this.submitCreate();
      return;
    }
    this.submitEdit();
  }

  private submitCreate(): void {
    this.submitting = true;
    this.bookingService
      .createReservation({
        habitacion_id: this.selectedRoom!.id,
        fecha_entrada: this.fechaEntrada!,
        fecha_salida: this.fechaSalida!,
        num_huespedes: this.numHuespedes,
        pago_id: null,
      })
      .subscribe({
        next: (res) => {
          this.toast.success(this.t.translate('createReservation.toastCreated'));
          this.submitting = false;
          this.router.navigate(['/bookings', res.id]);
        },
        error: (err: HttpErrorResponse) => {
          this.submitting = false;
          if (err.status === 409) {
            this.toast.warning(
              this.t.translate('createReservation.toastConflict')
            );
          } else {
            this.toast.danger(
              this.t.translate('createReservation.toastCreateError')
            );
          }
        },
      });
  }

  private submitEdit(): void {
    if (!this.reservaId || !this.initial) {
      return;
    }
    const body: UpdateBookingRequest = {};
    if (this.selectedRoom!.id !== this.initial.habitacionId) {
      body.habitacion_id = this.selectedRoom!.id;
    }
    if (this.fechaEntrada !== this.initial.fechaEntrada) {
      body.fecha_entrada = this.fechaEntrada!;
    }
    if (this.fechaSalida !== this.initial.fechaSalida) {
      body.fecha_salida = this.fechaSalida!;
    }
    if (this.numHuespedes !== this.initial.numHuespedes) {
      body.num_huespedes = this.numHuespedes;
    }
    if (Object.keys(body).length === 0) {
      return;
    }

    this.submitting = true;
    this.bookingService.updateReservation(this.reservaId, body).subscribe({
      next: () => {
        this.toast.success(this.t.translate('createReservation.toastUpdated'));
        this.submitting = false;
        this.router.navigate(['/bookings', this.reservaId!]);
      },
      error: (err: HttpErrorResponse) => {
        this.submitting = false;
        if (err.status === 409) {
          this.toast.warning(
            this.t.translate('createReservation.toastUpdateConflict')
          );
        } else if (err.status === 400) {
          this.toast.warning(
            this.t.translate('createReservation.toastUpdateInvalid')
          );
        } else {
          this.toast.danger(
            this.t.translate('createReservation.toastUpdateError')
          );
        }
      },
    });
  }

  onImageError(event: Event): void {
    const img = event.target as HTMLImageElement;
    img.src = this.placeholderImage;
  }

  get ctaKey(): string {
    if (this.mode === 'edit') {
      return this.submitting
        ? 'createReservation.saving'
        : 'createReservation.saveChanges';
    }
    return this.submitting
      ? 'createReservation.submitting'
      : 'createReservation.book';
  }
}
