import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { BookingService, BookingResponse } from '../../core/services/booking.service';
import { HotelService, HotelDetalle } from '../../core/services/hotel.service';
import { AuthService } from '../../core/services/auth.service';
import { forkJoin, of } from 'rxjs';
import { map, switchMap, catchError } from 'rxjs/operators';
import { RouterModule } from '@angular/router';

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
  private readonly hotelService = inject(HotelService);
  private readonly authService = inject(AuthService);
  private readonly dateFormat: Intl.DateTimeFormatOptions = {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  };

  activeTab: 'upcoming' | 'past' = 'upcoming';
  bookings: BookingDisplay[] = [];
  loading = true;

  ngOnInit(): void {
    this.loadBookings();
  }

  setTab(tab: 'upcoming' | 'past'): void {
    this.activeTab = tab;
  }

  loadBookings(): void {
    const user = this.authService.userProfile();
    if (!user) {
      this.loading = false;
      return;
    }

    this.loading = true;
    this.bookingService.getUserBookings(user.id, { limit: 50 }).pipe(
      switchMap((res) => {
        if (!res.reservas.length) return of([]);
        
        const bookingReqs = res.reservas.map(booking => {
          return this.hotelService.getRoomById(booking.habitacion_id).pipe(
            switchMap(room => {
               if(room.hotel_id) {
                 return this.hotelService.getHotelById(room.hotel_id).pipe(
                    map(hotel => this.mapToDisplay(booking, hotel)),
                    catchError(() => of(this.mapToDisplayFallback(booking)))
                 );
               }
               return of(this.mapToDisplayFallback(booking));
            }),
            catchError(() => of(this.mapToDisplayFallback(booking)))
          );
        });

        return forkJoin(bookingReqs);
      })
    ).subscribe({
      next: (data) => {
        this.bookings = data.filter(b => b.status === 'pendiente' || b.status === 'confirmada');
        this.loading = false;
      },
      error: () => {
        this.loading = false;
      }
    });
  }

  private mapToDisplay(booking: BookingResponse, hotel: HotelDetalle): BookingDisplay {
    const start = this.parseBackendDate(booking.fecha_entrada);
    const end = this.parseBackendDate(booking.fecha_salida);
    const nights = this.calculateNights(start, end);
    
    return {
      id: booking.id,
      hotelName: hotel.nombre,
      location: `${hotel.ciudad}, ${hotel.pais}`,
      image: hotel.imagenes?.[0] || 'assets/images/hotel3.avif',
      checkIn: this.formatDisplayDate(start),
      checkOut: this.formatDisplayDate(end),
      nights: nights,
      guests: booking.num_huespedes,
      status: booking.estado,
      statusLabel: booking.estado === 'confirmada' ? 'Confirmado' : 'Pendiente'
    };
  }

  private mapToDisplayFallback(booking: BookingResponse): BookingDisplay {
    const start = this.parseBackendDate(booking.fecha_entrada);
    const end = this.parseBackendDate(booking.fecha_salida);
    const nights = this.calculateNights(start, end);
    
    return {
      id: booking.id,
      hotelName: 'Hotel Desconocido',
      location: 'Ubicación Desconocida',
      image: 'assets/images/hotel3.avif',
      checkIn: this.formatDisplayDate(start),
      checkOut: this.formatDisplayDate(end),
      nights: nights,
      guests: booking.num_huespedes,
      status: booking.estado,
      statusLabel: booking.estado === 'confirmada' ? 'Confirmado' : 'Pendiente'
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
