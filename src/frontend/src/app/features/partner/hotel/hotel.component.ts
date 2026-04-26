import { Component } from '@angular/core';
import { RoomsTableComponent } from '../components/rooms-table/rooms-table.component';
import { TranslocoPipe } from '@jsverse/transloco';

@Component({
  selector: 'app-partner-hotel',
  standalone: true,
  imports: [RoomsTableComponent, TranslocoPipe],
  templateUrl: './hotel.component.html',
  styleUrl: './hotel.component.scss',
})
export class PartnerHotelComponent {

}
