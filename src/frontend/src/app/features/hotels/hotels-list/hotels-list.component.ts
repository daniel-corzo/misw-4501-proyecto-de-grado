import { Component, OnInit, inject } from '@angular/core';
import { RouterLink } from '@angular/router';
import { CommonModule } from '@angular/common';
import { HotelService, HotelListItem } from '../../../core/services/hotel.service';

@Component({
  selector: 'app-hotels-list',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './hotels-list.component.html',
  styleUrl: './hotels-list.component.scss',
})
export class HotelsListComponent implements OnInit {
  private readonly hotelService = inject(HotelService);

  hoteles: HotelListItem[] = [];
  total = 0;
  loading = true;
  error: string | null = null;

  ngOnInit(): void {
    this.hotelService.listHotels().subscribe({
      next: (res) => {
        this.hoteles = res.hoteles;
        this.total = res.total;
        this.loading = false;
      },
      error: () => {
        this.error = 'No se pudo cargar la lista de hoteles. Intente de nuevo más tarde.';
        this.loading = false;
      },
    });
  }
}
