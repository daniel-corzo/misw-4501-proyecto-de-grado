import { Component, OnInit, inject } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HotelService, HotelListItem, HotelListParams } from '../../../core/services/hotel.service';

const LIMIT = 10;

const POPULAR_AMENITIES = [
  { value: 'POOL', label: 'Swimming Pool' },
  { value: 'WIFI', label: 'Free WiFi' },
  { value: 'GYM', label: 'Fitness Center' },
  { value: 'SPA', label: 'Spa & Wellness' },
];

@Component({
  selector: 'app-hotels-list',
  standalone: true,
  imports: [CommonModule, RouterLink, FormsModule],
  templateUrl: './hotels-list.component.html',
  styleUrl: './hotels-list.component.scss',
})
export class HotelsListComponent implements OnInit {
  private readonly hotelService = inject(HotelService);
  private readonly route = inject(ActivatedRoute);

  readonly limit = LIMIT;
  readonly popularAmenities = POPULAR_AMENITIES;
  readonly starOptions = [5, 4, 3];
  readonly sortOptions: { value: NonNullable<HotelListParams['orden']>; label: string }[] = [
    { value: 'rating_desc', label: 'Recomendados' },
    { value: 'precio_asc', label: 'Precio ↑' },
    { value: 'precio_desc', label: 'Precio ↓' },
    { value: 'nombre_asc', label: 'Nombre A–Z' },
    { value: 'nombre_desc', label: 'Nombre Z–A' },
  ];

  // From URL params (display only)
  ciudad = '';
  checkIn = '';
  checkOut = '';
  huespedes = 1;

  // Filters — rango en COP para coincidir con los datos del seed
  readonly PRICE_MIN = 50000;
  readonly PRICE_MAX = 3000000;
  readonly PRICE_STEP = 50000;
  readonly PRICE_GAP = 100000;
  precioMin = 50000;
  precioMax = 3000000;
  selectedStars: Set<number> = new Set();
  selectedAmenidades: Set<string> = new Set();

  get priceMinPct(): number {
    return ((this.precioMin - this.PRICE_MIN) / (this.PRICE_MAX - this.PRICE_MIN)) * 100;
  }

  get priceMaxPct(): number {
    return ((this.precioMax - this.PRICE_MIN) / (this.PRICE_MAX - this.PRICE_MIN)) * 100;
  }

  onPriceMinInput(): void {
    if (this.precioMin > this.precioMax - this.PRICE_GAP) {
      this.precioMin = Math.max(this.PRICE_MIN, this.precioMax - this.PRICE_GAP);
    }
    this.onPriceChange();
  }

  onPriceMaxInput(): void {
    if (this.precioMax < this.precioMin + this.PRICE_GAP) {
      this.precioMax = Math.min(this.PRICE_MAX, this.precioMin + this.PRICE_GAP);
    }
    this.onPriceChange();
  }

  // Sort / pagination
  orden: NonNullable<HotelListParams['orden']> = 'rating_desc';
  page = 0;

  // Results
  hoteles: HotelListItem[] = [];
  total = 0;
  loading = false;
  error: string | null = null;
  imageErrors = new Set<string>();

  private priceDebounce: ReturnType<typeof setTimeout> | null = null;

  get totalPages(): number {
    return Math.max(1, Math.ceil(this.total / this.limit));
  }

  get visiblePages(): (number | '...')[] {
    const total = this.totalPages;
    if (total <= 7) return Array.from({ length: total }, (_, i) => i);
    const pages: (number | '...')[] = [0];
    if (this.page > 2) pages.push('...');
    for (let i = Math.max(1, this.page - 1); i <= Math.min(total - 2, this.page + 1); i++) {
      pages.push(i);
    }
    if (this.page < total - 3) pages.push('...');
    pages.push(total - 1);
    return pages;
  }

  get dateRangeLabel(): string {
    if (this.checkIn && this.checkOut) return `${this.checkIn} – ${this.checkOut}`;
    return '';
  }

  ngOnInit(): void {
    this.route.queryParams.subscribe(params => {
      this.ciudad = params['ciudad'] || '';
      this.checkIn = params['checkIn'] || '';
      this.checkOut = params['checkOut'] || '';
      this.huespedes = params['huespedes'] ? Number(params['huespedes']) : 1;
      this.page = 0;
      this.loadHotels();
    });
  }

  loadHotels(): void {
    this.loading = true;
    this.error = null;

    const params: HotelListParams = {
      limit: this.limit,
      offset: this.page * this.limit,
      orden: this.orden,
    };

    if (this.ciudad) params.ciudad = this.ciudad;
    if (this.precioMin > this.PRICE_MIN) params.precio_min = this.precioMin;
    if (this.precioMax < this.PRICE_MAX) params.precio_max = this.precioMax;
    if (this.selectedStars.size > 0) params.estrellas = Array.from(this.selectedStars);
    if (this.selectedAmenidades.size > 0) params.amenidades_populares = Array.from(this.selectedAmenidades);
    if (this.huespedes > 1) params.capacidad_min = this.huespedes;

    this.hotelService.listHotels(params).subscribe({
      next: res => {
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

  onPriceChange(): void {
    if (this.priceDebounce) clearTimeout(this.priceDebounce);
    this.priceDebounce = setTimeout(() => {
      this.page = 0;
      this.loadHotels();
    }, 300);
  }

  toggleStar(star: number): void {
    if (this.selectedStars.has(star)) {
      this.selectedStars.delete(star);
    } else {
      this.selectedStars.add(star);
    }
    this.selectedStars = new Set(this.selectedStars);
    this.page = 0;
    this.loadHotels();
  }

  toggleAmenidad(value: string): void {
    if (this.selectedAmenidades.has(value)) {
      this.selectedAmenidades.delete(value);
    } else {
      this.selectedAmenidades.add(value);
    }
    this.selectedAmenidades = new Set(this.selectedAmenidades);
    this.page = 0;
    this.loadHotels();
  }

  onOrdenChange(): void {
    this.page = 0;
    this.loadHotels();
  }

  goToPage(p: number | '...'): void {
    if (p === '...') return;
    if (p < 0 || p >= this.totalPages) return;
    this.page = p;
    this.loadHotels();
  }

  clearFilters(): void {
    this.precioMin = this.PRICE_MIN;
    this.precioMax = this.PRICE_MAX;
    this.selectedStars = new Set();
    this.selectedAmenidades = new Set();
    this.orden = 'rating_desc';
    this.page = 0;
    this.loadHotels();
  }

  hasAmenidad(hotel: HotelListItem, value: string): boolean {
    return hotel.amenidades?.includes(value) ?? false;
  }

  getStars(count: number): boolean[] {
    return Array.from({ length: 5 }, (_, i) => i < count);
  }

  getImageUrl(hotel: HotelListItem): string {
    return hotel.imagenes?.[0] || '';
  }

  hasValidImage(hotel: HotelListItem): boolean {
    return !!this.getImageUrl(hotel) && !this.imageErrors.has(hotel.id);
  }

  onImageError(hotelId: string): void {
    this.imageErrors.add(hotelId);
    this.imageErrors = new Set(this.imageErrors);
  }
}
