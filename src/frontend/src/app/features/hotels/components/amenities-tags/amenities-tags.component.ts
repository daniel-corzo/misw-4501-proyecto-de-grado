import { Component, Input, forwardRef } from '@angular/core';
import { ControlValueAccessor, NG_VALUE_ACCESSOR } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { TranslocoPipe } from '@jsverse/transloco';

export const AMENITIES_LIST = [
  { value: 'POOL', label: 'Pool' },
  { value: 'GYM', label: 'Gym' },
  { value: 'SPA', label: 'Spa' },
  { value: 'RESTAURANT', label: 'Restaurant' },
  { value: 'BAR', label: 'Bar' },
  { value: 'WIFI', label: 'Wi-Fi' },
  { value: 'PARKING', label: 'Parking' },
  { value: 'AIR_CONDITIONING', label: 'Air Conditioning' },
  { value: 'ROOM_SERVICE', label: 'Room Service' },
  { value: 'LAUNDRY', label: 'Laundry' },
  { value: 'CONCIERGE', label: 'Concierge' },
  { value: 'BEACH_ACCESS', label: 'Beach Access' },
  { value: 'SKI_ACCESS', label: 'Ski Access' },
  { value: 'PET_FRIENDLY', label: 'Pet Friendly' },
  { value: 'SMOKING_AREA', label: 'Smoking Area' },
  { value: 'EV_CHARGING', label: 'EV Charging' },
  { value: 'BUSINESS_CENTER', label: 'Business Center' },
  { value: 'CONFERENCE_ROOM', label: 'Conference Room' },
  { value: 'CHILDREN_PLAYGROUND', label: 'Children Playground' },
  { value: 'SHUTTLE', label: 'Shuttle Service' },
  { value: 'BREAKFAST_INCLUDED', label: 'Breakfast Included' }
];

@Component({
  selector: 'app-amenities-tags',
  standalone: true,
  imports: [CommonModule, TranslocoPipe],
  templateUrl: './amenities-tags.component.html',
  styleUrl: './amenities-tags.component.scss',
  providers: [
    {
      provide: NG_VALUE_ACCESSOR,
      useExisting: forwardRef(() => AmenitiesTagsComponent),
      multi: true
    }
  ]
})
export class AmenitiesTagsComponent implements ControlValueAccessor {
  @Input() editable = false;
  @Input() error: string | null = null;
  @Input() amenities: string[] = []; // Used when readonly, or for initial state

  readonly availableAmenities = AMENITIES_LIST;
  
  selectedAmenities: Set<string> = new Set();
  disabled = false;

  private onChange: (value: string) => void = () => {};
  private onTouched: () => void = () => {};

  writeValue(value: any): void {
    if (Array.isArray(value)) {
      this.selectedAmenities = new Set(value);
    } else if (typeof value === 'string' && value.trim()) {
      this.selectedAmenities = new Set(value.split(',').map(s => s.trim()));
    } else {
      this.selectedAmenities = new Set(this.amenities || []);
    }
  }

  registerOnChange(fn: any): void {
    this.onChange = (val) => {
      const arr = Array.from(this.selectedAmenities);
      // For string form controls or array. Assuming it emits comma separated string based on usual backend needs or arrays depending on requirements.
      // Let's emit a comma-separated string because it maps well to simple inputs, but it depends on what the form control expects string[] vs string.
      // Usually amenities are an array. Let's emit an array of values, or a comma separated string.
      // E.g. "POOL,WIFI" vs ["POOL", "WIFI"]. The model has amenities: ['', [Validators.required]] which implies a string. Let's emit string.
      fn(arr.join(','));
    };
  }

  registerOnTouched(fn: any): void {
    this.onTouched = fn;
  }

  setDisabledState?(isDisabled: boolean): void {
    this.disabled = isDisabled;
  }

  toggleAmenity(value: string) {
    if (!this.editable || this.disabled) return;
    
    if (this.selectedAmenities.has(value)) {
      this.selectedAmenities.delete(value);
    } else {
      this.selectedAmenities.add(value);
    }
    
    this.onTouched();
    
    const arr = Array.from(this.selectedAmenities);
    this.onChange(arr.join(','));
  }

  isSelected(value: string): boolean {
    if (!this.editable && this.amenities && this.amenities.length > 0 && this.selectedAmenities.size === 0) {
      return this.amenities.includes(value);
    }
    return this.selectedAmenities.has(value);
  }
}