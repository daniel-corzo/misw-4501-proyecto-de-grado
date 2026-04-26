import { Component, inject } from '@angular/core';
import { Location } from '@angular/common';
import { RouterLink } from '@angular/router';
import { TranslocoPipe } from '@jsverse/transloco';

@Component({
  selector: 'app-terms',
  standalone: true,
  imports: [RouterLink, TranslocoPipe],
  templateUrl: './terms.component.html',
  styleUrl: './terms.component.scss',
})
export class TermsComponent {
  private readonly location = inject(Location);

  goBack(): void {
    this.location.back();
  }
}
