import { Component } from '@angular/core';
import { RoomsTableComponent } from '../components/rooms-table/rooms-table.component';

@Component({
  selector: 'app-partner-hotel',
  standalone: true,
  imports: [RoomsTableComponent],
  templateUrl: './hotel.component.html',
  styleUrl: './hotel.component.scss',
})
export class PartnerHotelComponent {

}
