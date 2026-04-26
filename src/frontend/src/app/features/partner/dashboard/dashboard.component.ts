import { Component } from '@angular/core';
import { TranslocoPipe } from '@jsverse/transloco';

@Component({
  selector: 'app-partner-dashboard',
  standalone: true,
  imports: [TranslocoPipe],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.scss',
})
export class PartnerDashboardComponent {}
