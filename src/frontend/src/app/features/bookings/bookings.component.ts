import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { BookingService, BookingResponse, BookingFilter } from '../../core/services/booking.service';
import { AuthService } from '../../core/services/auth.service';
import { RouterModule } from '@angular/router';
import { PLACEHOLDER_IMAGE } from '../../shared/constants/images';

interface BookingDisplay {
  id: string;
  hotelName: string;
  location: string;
  image: string;
  checkIn: string;
  checkOut: string;
  nights: number;
  guests: number;
  status: string;
  statusLabel: string;
}

@Component({
  selector: 'app-bookings',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './bookings.component.html',
  styleUrl: './bookings.component.scss',
})
export class BookingsComponent implements OnInit {
  private readonly bookingService = inject(BookingService);
  private readonly dateFormat: Intl.DateTimeFormatOptions = {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  };

  activeTab: 'upcoming' | 'past' | 'cancelled' = 'upcoming';
  bookings: BookingDisplay[] = [];
  loading = true;

  readonly placeholderImage = PLACEHOLDER_IMAGE;

  private readonly statusLabels: Record<string, string> = {
    confirmada: 'Confirmado',
    pendiente: 'Pendiente',
    cancelada: 'Cancelada',
    completada: 'Completada',
  };

  ngOnInit(): void {
    this.loadBookings();
  }

  setTab(tab: 'upcoming' | 'past' | 'cancelled'): void {
    this.activeTab = tab;
    this.loadBookings();
  }

  loadBookings(): void {
    this.loading = true;
    this.bookings = [];

    const statusMap: Record<typeof this.activeTab, BookingFilter> = {
      upcoming: 'activas',
      past: 'pasadas',
      cancelled: 'canceladas',
    };

    this.bookingService.getBookingsByStatus(statusMap[this.activeTab]).subscribe({
      next: (res) => {
        this.bookings = res.reservas.map(b => this.mapToDisplay(b));
        this.loading = false;
      },
      error: () => {
        this.loading = false;
      }
    });
  }

  onImageError(event: Event): void {
    const img = event.target as HTMLImageElement;
    img.src = this.placeholderImage;
  }

  private mapToDisplay(booking: BookingResponse): BookingDisplay {
    const start = this.parseBackendDate(booking.fecha_entrada);
    const end = this.parseBackendDate(booking.fecha_salida);
    const nights = this.calculateNights(start, end);
    const image = booking.imagenes_hotel?.[0] || this.placeholderImage;
    const city = booking.ciudad_hotel ?? '';
    const country = booking.pais_hotel ?? '';
    const location = city && country ? `${city}, ${country}` : city || country || 'Ubicación Desconocida';

    return {
      id: booking.id,
      hotelName: booking.nombre_hotel || 'Hotel Desconocido',
      location,
      image,
      checkIn: this.formatDisplayDate(start),
      checkOut: this.formatDisplayDate(end),
      nights,
      guests: booking.num_huespedes,
      status: booking.estado,
      statusLabel: this.statusLabels[booking.estado] ?? booking.estado,
    };
  }

  private parseBackendDate(value: string): Date {
    const match = /^(\d{4})-(\d{2})-(\d{2})$/.exec(value);
    if (match) {
      const year = Number(match[1]);
      const monthIndex = Number(match[2]) - 1;
      const day = Number(match[3]);
      return new Date(year, monthIndex, day);
    }
    return new Date(value);
  }

  private formatDisplayDate(date: Date): string {
    return date.toLocaleDateString('es-ES', this.dateFormat);
  }

  private calculateNights(start: Date, end: Date): number {
    const startUtc = Date.UTC(start.getFullYear(), start.getMonth(), start.getDate());
    const endUtc = Date.UTC(end.getFullYear(), end.getMonth(), end.getDate());
    return Math.max(0, Math.round((endUtc - startUtc) / (1000 * 60 * 60 * 24)));
  }

  printVoucher(booking: BookingDisplay): void {
    const win = window.open('', '', 'width=600,height=600');
    if (!win) return;

    const doc = win.document;
    doc.title = 'Voucher';
    doc.documentElement.lang = 'es';

    while (doc.body.firstChild) {
      doc.body.removeChild(doc.body.firstChild);
    }

    while (doc.head.firstChild) {
      doc.head.removeChild(doc.head.firstChild);
    }

    const style = doc.createElement('style');
    style.textContent = `
      body { font-family: Arial, sans-serif; padding: 24px; }
      h1 { margin-bottom: 16px; }
      p { margin: 8px 0; }
      strong { display: inline-block; min-width: 110px; }
    `;
    doc.head.appendChild(style);

    const title = doc.createElement('h1');
    title.textContent = 'Voucher de Reserva';
    doc.body.appendChild(title);

    const appendField = (label: string, value: string): void => {
      const row = doc.createElement('p');
      const key = doc.createElement('strong');
      key.textContent = `${label}:`;
      row.appendChild(key);
      row.appendChild(doc.createTextNode(` ${value}`));
      doc.body.appendChild(row);
    };

    appendField('ID Reserva', booking.id);
    appendField('Hotel', booking.hotelName);
    appendField('Lugar', booking.location);
    appendField('Check-in', booking.checkIn);
    appendField('Check-out', booking.checkOut);
    appendField('Huéspedes', `${booking.guests} Adultos`);
    appendField('Estado', booking.statusLabel);

    win.print();
  }
}
