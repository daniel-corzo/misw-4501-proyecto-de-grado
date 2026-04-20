import { Component, OnInit, inject } from '@angular/core';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HotelService, HotelListItem, HotelListParams } from '../../../core/services/hotel.service';

const LIMIT = 10;

const POPULAR_AMENITIES = [
  { value: 'POOL', label: 'Piscina' },
  { value: 'WIFI', label: 'WiFi gratis' },
  { value: 'BREAKFAST_INCLUDED', label: 'Desayuno incluido' },
  { value: 'PARKING', label: 'Parqueadero' },
];

const POPULAR_AMENITY_VALUES = new Set(POPULAR_AMENITIES.map(a => a.value));

const ALL_AMENITIES = [
  ...POPULAR_AMENITIES,
  { value: 'GYM', label: 'Gimnasio' },
  { value: 'SPA', label: 'Spa y bienestar' },
  { value: 'RESTAURANT', label: 'Restaurante' },
  { value: 'BAR', label: 'Bar' },
  { value: 'AIR_CONDITIONING', label: 'Aire acondicionado' },
  { value: 'ROOM_SERVICE', label: 'Servicio a la habitación' },
  { value: 'LAUNDRY', label: 'Lavandería' },
  { value: 'CONCIERGE', label: 'Conserje' },
  { value: 'BEACH_ACCESS', label: 'Acceso a playa' },
  { value: 'SKI_ACCESS', label: 'Acceso a esquí' },
  { value: 'PET_FRIENDLY', label: 'Admite mascotas' },
  { value: 'SMOKING_AREA', label: 'Zona de fumadores' },
  { value: 'EV_CHARGING', label: 'Carga eléctrica' },
  { value: 'BUSINESS_CENTER', label: 'Centro de negocios' },
  { value: 'CONFERENCE_ROOM', label: 'Sala de conferencias' },
  { value: 'CHILDREN_PLAYGROUND', label: 'Parque infantil' },
  { value: 'SHUTTLE', label: 'Transporte' },
];

const EXTRA_AMENITIES = ALL_AMENITIES.filter(a => !POPULAR_AMENITY_VALUES.has(a.value));

const AMENIDAD_LABELS: Record<string, string> = {
  POOL: 'Piscina',
  GYM: 'Gimnasio',
  SPA: 'Spa',
  RESTAURANT: 'Restaurante',
  BAR: 'Bar',
  WIFI: 'WiFi gratis',
  PARKING: 'Parqueadero',
  AIR_CONDITIONING: 'Aire acondicionado',
  ROOM_SERVICE: 'Servicio a la habitación',
  LAUNDRY: 'Lavandería',
  CONCIERGE: 'Conserje',
  BEACH_ACCESS: 'Acceso a playa',
  SKI_ACCESS: 'Acceso a esquí',
  PET_FRIENDLY: 'Admite mascotas',
  SMOKING_AREA: 'Zona de fumadores',
  EV_CHARGING: 'Carga eléctrica',
  BUSINESS_CENTER: 'Centro de negocios',
  CONFERENCE_ROOM: 'Sala de conferencias',
  CHILDREN_PLAYGROUND: 'Parque infantil',
  SHUTTLE: 'Transporte',
  BREAKFAST_INCLUDED: 'Desayuno incluido',
};

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
  private readonly router = inject(Router);

  readonly limit = LIMIT;
  readonly popularAmenities = POPULAR_AMENITIES;
  readonly extraAmenities = EXTRA_AMENITIES;
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

  // Countries for dropdown
  paises: string[] = [];
  selectedPais = '';

  // Amenities expand toggle
  showAllAmenities = false;

  // Results
  hoteles: HotelListItem[] = [];
  total = 0;
  loading = false;
  error: string | null = null;
  imageErrors = new Set<string>();

  private priceDebounce: ReturnType<typeof setTimeout> | null = null;
  private cityDebounce: ReturnType<typeof setTimeout> | null = null;

  get today(): string {
    return new Date().toISOString().split('T')[0];
  }

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
    this.hotelService.listCountries().subscribe({
      next: res => { this.paises = res.paises; },
    });

    this.route.queryParams.subscribe(params => {
      this.ciudad = params['ciudad'] || '';
      this.checkIn = params['checkIn'] || '';
      this.checkOut = params['checkOut'] || '';
      this.huespedes = params['huespedes'] ? Number(params['huespedes']) : 1;
      this.selectedPais = this.paises.includes(this.ciudad) ? this.ciudad : '';
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

  onCityInput(): void {
    if (this.cityDebounce) clearTimeout(this.cityDebounce);
    this.selectedPais = '';
    this.cityDebounce = setTimeout(() => this.applyCityFilter(), 400);
  }

  onCitySubmit(event: Event): void {
    event.preventDefault();
    if (this.cityDebounce) clearTimeout(this.cityDebounce);
    this.applyCityFilter();
  }

  onPaisChange(): void {
    this.ciudad = this.selectedPais;
    this.applyCityFilter();
  }

  private applyCityFilter(): void {
    this.router.navigate([], {
      relativeTo: this.route,
      queryParams: { ciudad: this.ciudad || null },
      queryParamsHandling: 'merge',
    });
    // loadHotels() se dispara vía queryParams.subscribe en ngOnInit
  }

  decrementHuespedes(): void {
    if (this.huespedes > 1) {
      this.huespedes--;
      this.syncHuespedes();
    }
  }

  incrementHuespedes(): void {
    if (this.huespedes < 20) {
      this.huespedes++;
      this.syncHuespedes();
    }
  }

  private syncHuespedes(): void {
    this.router.navigate([], {
      relativeTo: this.route,
      queryParams: { huespedes: this.huespedes > 1 ? this.huespedes : null },
      queryParamsHandling: 'merge',
    });
    this.page = 0;
    this.loadHotels();
  }

  onDateChange(): void {
    const checkOutMin = this.checkIn
      ? new Date(new Date(this.checkIn).getTime() + 86400000).toISOString().split('T')[0]
      : '';
    if (this.checkOut && this.checkOut <= this.checkIn) {
      this.checkOut = checkOutMin;
    }
    this.router.navigate([], {
      relativeTo: this.route,
      queryParams: {
        checkIn: this.checkIn || null,
        checkOut: this.checkOut || null,
      },
      queryParamsHandling: 'merge',
    });
    // Las fechas aún no se envían al backend (disponibilidad por fechas pendiente con equipo)
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

  getAmenidadLabel(value: string): string {
    return AMENIDAD_LABELS[value] ?? value;
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
