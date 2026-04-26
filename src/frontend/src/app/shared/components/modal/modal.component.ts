import { Component, input, output } from '@angular/core';
import { TranslocoPipe } from '@jsverse/transloco';

@Component({
  selector: 'app-modal',
  standalone: true,
  imports: [TranslocoPipe],
  templateUrl: './modal.component.html',
  styleUrl: './modal.component.scss',
})
export class ModalComponent {
  wide = input(false);
  title = input<string>();
  closed = output();
}
