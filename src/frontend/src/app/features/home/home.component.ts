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
    return this.formatLocalDate(new Date());
  }

  get checkOutMin(): string {
    if (!this.checkIn) {
      return this.today;
    }
    return this.formatLocalDate(this.addDays(this.parseDateOnlyLocal(this.checkIn), 1));
  }

  onDateChange(): void {
    const checkOutMin = this.checkOutMin;

    if (this.checkOut && this.checkOut <= this.checkIn) {
      this.checkOut = checkOutMin;
    }
  }

  private parseDateOnlyLocal(value: string): Date {
    const [year, month, day] = value.split('-').map(Number);
    return new Date(year, month - 1, day);
  }

  private addDays(date: Date, days: number): Date {
    return new Date(date.getFullYear(), date.getMonth(), date.getDate() + days);
  }

  private formatLocalDate(date: Date): string {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
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
