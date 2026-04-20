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
    if (!user) return;

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
    const start = new Date(booking.fecha_entrada);
    const end = new Date(booking.fecha_salida);
    const nights = Math.ceil((end.getTime() - start.getTime()) / (1000 * 60 * 60 * 24));
    
    return {
      id: booking.id,
      hotelName: hotel.nombre,
      location: `${hotel.ciudad}, ${hotel.pais}`,
      image: hotel.imagenes?.[0] || 'assets/images/hotel3.avif',
      checkIn: start.toLocaleDateString('es-ES', { month: 'short', day: 'numeric', year: 'numeric' }),
      checkOut: end.toLocaleDateString('es-ES', { month: 'short', day: 'numeric', year: 'numeric' }),
      nights: nights,
      guests: booking.num_huespedes,
      status: booking.estado,
      statusLabel: booking.estado === 'confirmada' ? 'Confirmado' : 'Pendiente'
    };
  }

  private mapToDisplayFallback(booking: BookingResponse): BookingDisplay {
    const start = new Date(booking.fecha_entrada);
    const end = new Date(booking.fecha_salida);
    const nights = Math.ceil((end.getTime() - start.getTime()) / (1000 * 60 * 60 * 24));
    
    return {
      id: booking.id,
      hotelName: 'Hotel Desconocido',
      location: 'Ubicación Desconocida',
      image: 'assets/images/hotel3.avif',
      checkIn: start.toLocaleDateString('es-ES', { month: 'short', day: 'numeric', year: 'numeric' }),
      checkOut: end.toLocaleDateString('es-ES', { month: 'short', day: 'numeric', year: 'numeric' }),
      nights: nights,
      guests: booking.num_huespedes,
      status: booking.estado,
      statusLabel: booking.estado === 'confirmada' ? 'Confirmado' : 'Pendiente'
    };
  }

  printVoucher(booking: BookingDisplay): void {
    const content = `
      <h1>Voucher de Reserva</h1>
      <p><strong>ID Reserva:</strong> ${booking.id}</p>
      <p><strong>Hotel:</strong> ${booking.hotelName}</p>
      <p><strong>Lugar:</strong> ${booking.location}</p>
      <p><strong>Check-in:</strong> ${booking.checkIn}</p>
      <p><strong>Check-out:</strong> ${booking.checkOut}</p>
      <p><strong>Huéspedes:</strong> ${booking.guests} Adultos</p>
      <p><strong>Estado:</strong> ${booking.statusLabel}</p>
    `;
    const win = window.open('', '', 'width=600,height=600');
    if (win) {
      win.document.write('<html><head><title>Voucher</title></head><body>' + content + '</body></html>');
      win.document.close();
      win.print();
    }
  }
}
