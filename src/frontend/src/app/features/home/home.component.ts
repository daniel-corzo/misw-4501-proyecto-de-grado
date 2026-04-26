import { Component, inject } from '@angular/core';
import { Router } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { TranslocoPipe } from '@jsverse/transloco';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [FormsModule, TranslocoPipe],
  templateUrl: './home.component.html',
  styleUrl: './home.component.scss',
})
export class HomeComponent {
  private readonly router = inject(Router);

  ciudad = '';
  checkIn = '';
  checkOut = '';
  huespedes = 2;

  get today(): string {
    return new Date().toISOString().split('T')[0];
  }

  onDateChange(): void {
    const checkOutMin = this.checkIn
      ? new Date(new Date(this.checkIn).getTime() + 86400000).toISOString().split('T')[0]
      : '';

    if (this.checkOut && this.checkOut <= this.checkIn) {
      this.checkOut = checkOutMin;
    }
  }

  buscar(): void {
    const queryParams: Record<string, string | number> = {};
    if (this.ciudad) queryParams['ciudad'] = this.ciudad;
    if (this.checkIn) queryParams['checkIn'] = this.checkIn;
    if (this.checkOut) queryParams['checkOut'] = this.checkOut;
    if (this.huespedes && this.huespedes > 1) queryParams['huespedes'] = this.huespedes;
    this.router.navigate(['/hotels'], { queryParams });
  }
}
