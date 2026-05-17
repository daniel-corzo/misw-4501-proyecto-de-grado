import { CommonModule } from '@angular/common';
import { HttpErrorResponse } from '@angular/common/http';
import { Component, OnInit, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { TranslocoPipe, TranslocoService } from '@jsverse/transloco';
import { Observable, Subject } from 'rxjs';

import { BookingService } from '../../../core/services/booking.service';
import { PaymentService } from '../../../core/services/payment.service';
import { ToastService } from '../../../core/services/toast.service';
import { PLACEHOLDER_IMAGE } from '../../../shared/constants/images';

export interface CheckoutState {
  bookingId: string;
  hotelId: string;
  hotelNombre: string;
  hotelImagen: string | null;
  hotelEstrellas: number | null;
  fechaEntrada: string;
  fechaSalida: string;
  numHuespedes: number;
  habitacionId: string;
  subtotal: number;
  taxes: number;
  total: number;
  stayNights: number;
}

@Component({
  selector: 'app-checkout',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink, TranslocoPipe],
  templateUrl: './checkout.component.html',
  styleUrl: './checkout.component.scss',
})
export class CheckoutComponent implements OnInit {
  private readonly router = inject(Router);
  private readonly bookingService = inject(BookingService);
  private readonly paymentService = inject(PaymentService);
  private readonly toast = inject(ToastService);
  private readonly t = inject(TranslocoService);

  state: CheckoutState | null = null;
  missingData = false;

  cardholderName = '';
  cardNumber = '';
  expirationDate = '';
  cvc = '';
  termsAccepted = false;

  expirationTouched = false;

  submitting = false;
  paymentCompleted = false;
  showLeaveDialog = false;
  isLeaveCancelling = false;
  private leaveSubject: Subject<boolean> | null = null;

  readonly placeholderImage = PLACEHOLDER_IMAGE;

  ngOnInit(): void {
    const nav = this.router.getCurrentNavigation();
    const s = (nav?.extras?.state ?? window.history.state) as Partial<CheckoutState> | null;

    if (!this.isValidCheckoutState(s)) {
      this.missingData = true;
      return;
    }

    this.state = s;
  }

  private isValidCheckoutState(s: Partial<CheckoutState> | null): s is CheckoutState {
    return (
      !!s &&
      !!s.bookingId &&
      !!s.hotelId &&
      !!s.habitacionId &&
      !!s.fechaEntrada &&
      !!s.fechaSalida &&
      typeof s.subtotal === 'number' &&
      Number.isFinite(s.subtotal) &&
      typeof s.taxes === 'number' &&
      Number.isFinite(s.taxes) &&
      typeof s.total === 'number' &&
      Number.isFinite(s.total) &&
      typeof s.stayNights === 'number' &&
      Number.isFinite(s.stayNights) &&
      s.stayNights > 0
    );
  }

  // ── Formatters ──────────────────────────────────────────────────────────

  onCardNumberInput(): void {
    const digits = this.cardNumber.replace(/\D/g, '').slice(0, 16);
    this.cardNumber = digits.replace(/(.{4})/g, '$1 ').trim();
  }

  onExpirationInput(): void {
    const digits = this.expirationDate.replace(/\D/g, '').slice(0, 4);
    if (digits.length <= 2) {
      this.expirationDate = digits;
    } else {
      this.expirationDate = `${digits.slice(0, 2)}/${digits.slice(2)}`;
    }
    this.expirationTouched = true;
  }

  onCvcInput(): void {
    this.cvc = this.cvc.replace(/\D/g, '').slice(0, 3);
  }

  // ── Validation ──────────────────────────────────────────────────────────

  get cardNumberDigits(): string {
    return this.cardNumber.replace(/\s/g, '');
  }

  get cardNumberValid(): boolean {
    return this.cardNumberDigits.length === 16;
  }

  get expirationValid(): boolean {
    return this.expirationDateIsValid(this.expirationDate);
  }

  get expirationError(): string | null {
    if (!this.expirationTouched || this.expirationDate.length === 0) return null;
    const parts = this.expirationDate.split('/');
    if (parts.length === 2 && parts[0].length === 2 && parts[1].length === 2) {
      const month = parseInt(parts[0], 10);
      const year = parseInt(parts[1], 10);
      const now = new Date();
      const currentYear = now.getFullYear() % 100;
      const currentMonth = now.getMonth() + 1;
      if (month < 1 || month > 12) {
        return this.t.translate('checkout.errors.expirationInvalid');
      }
      if (year < currentYear || (year === currentYear && month < currentMonth)) {
        return this.t.translate('checkout.errors.expirationExpired');
      }
      return null;
    }
    if (!this.expirationValid) {
      return this.t.translate('checkout.errors.expirationInvalid');
    }
    return null;
  }

  get cvcValid(): boolean {
    return this.cvc.length === 3;
  }

  get formValid(): boolean {
    return (
      this.cardholderName.trim().length > 0 &&
      this.cardNumberValid &&
      this.expirationValid &&
      this.cvcValid &&
      this.termsAccepted
    );
  }

  get isButtonDisabled(): boolean {
    return this.submitting || !this.formValid;
  }

  /**
   * Mirrors PaymentDetailView+ViewModel.expirationDateIsValid:
   * - If only MM part typed: month must be 1-12.
   * - If MM/YY: month 1-12, year >= currentYear (2-digit), and if same year month >= currentMonth.
   */
  private expirationDateIsValid(value: string): boolean {
    if (!value || value.trim().length === 0) return false;

    const parts = value.split('/');

    if (parts.length === 1) {
      const month = parseInt(parts[0], 10);
      if (isNaN(month) || month < 1 || month > 12) return false;
      return true;
    }

    if (parts.length === 2) {
      const month = parseInt(parts[0], 10);
      const year = parseInt(parts[1], 10);
      if (isNaN(month) || isNaN(year)) return false;
      if (month < 1 || month > 12) return false;

      const now = new Date();
      const currentYear = now.getFullYear() % 100;
      const currentMonth = now.getMonth() + 1;

      if (year < currentYear) return false;
      if (year === currentYear && month < currentMonth) return false;
      return true;
    }

    return false;
  }

  // ── Submit ──────────────────────────────────────────────────────────────

  onSubmit(): void {
    if (!this.formValid || !this.state || this.submitting) return;

    this.submitting = true;

    this.paymentService
      .pay({
        cardholderName: this.cardholderName,
        cardNumber: this.cardNumber,
        cvv: this.cvc,
        expirationDate: this.expirationDate,
        monto: this.state.total,
      })
      .subscribe({
        next: (payment) => {
          this.linkPayment(payment.id);
        },
        error: (err: unknown) => {
          this.submitting = false;
          console.error('[Checkout] Payment error:', err);
          this.cancelBookingAndNotify();
          this.toast.danger(this.t.translate('checkout.toastPaymentError'));
        },
      });
  }

  private linkPayment(pagoId: string): void {
    const s = this.state!;
    this.bookingService
      .updateReservation(s.bookingId, { pago_id: pagoId })
      .subscribe({
        next: () => {
          this.submitting = false;
          this.paymentCompleted = true;
          this.router.navigate(['/bookings', s.bookingId]);
        },
        error: (err: HttpErrorResponse) => {
          this.submitting = false;
          console.error('[Checkout] Link payment error:', err);
          this.cancelBookingAndNotify();
          this.toast.danger(this.t.translate('checkout.toastBookingError'));
        },
      });
  }

  private cancelBookingAndNotify(): void {
    const bookingId = this.state?.bookingId;
    if (!bookingId) return;
    this.bookingService.deleteReservation(bookingId).subscribe({
      error: (err: unknown) =>
        console.error('[Checkout] Failed to delete booking after error:', err),
    });
  }

  canDeactivate(): Observable<boolean> | boolean {
    if (!this.state?.bookingId || this.paymentCompleted) return true;
    this.showLeaveDialog = true;
    this.leaveSubject = new Subject<boolean>();
    return this.leaveSubject.asObservable();
  }

  confirmLeave(): void {
    this.isLeaveCancelling = true;
    this.cancelBookingAndNotify();
    this.leaveSubject?.next(true);
    this.leaveSubject?.complete();
    this.showLeaveDialog = false;
  }

  cancelLeave(): void {
    this.leaveSubject?.next(false);
    this.leaveSubject?.complete();
    this.showLeaveDialog = false;
  }

  // ── Helpers ─────────────────────────────────────────────────────────────

  formatPrice(amount: number): string {
    return amount.toLocaleString(this.t.getActiveLang() === 'en' ? 'en-US' : 'es-CO');
  }

  stars(n: number | null): number[] {
    return Array.from({ length: n ?? 0 }, (_, i) => i);
  }

  onImageError(event: Event): void {
    const img = event.target as HTMLImageElement;
    img.src = this.placeholderImage;
  }
}
