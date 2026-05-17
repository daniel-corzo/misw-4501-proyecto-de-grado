import { Component } from '@angular/core';

@Component({
  selector: 'app-color-blind-filters',
  standalone: true,
  template: `
    <svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false">
      <defs>
        <filter id="cb-protanopia">
          <feColorMatrix type="matrix"
            values="0.567 0.433 0 0 0
                    0.558 0.442 0 0 0
                    0     0.242 0.758 0 0
                    0     0     0     1 0" />
        </filter>
        <filter id="cb-deuteranopia">
          <feColorMatrix type="matrix"
            values="0.625 0.375 0 0 0
                    0.7   0.3   0 0 0
                    0     0.3   0.7 0 0
                    0     0     0   1 0" />
        </filter>
        <filter id="cb-tritanopia">
          <feColorMatrix type="matrix"
            values="0.95  0.05  0     0 0
                    0     0.433 0.567 0 0
                    0     0.475 0.525 0 0
                    0     0     0     1 0" />
        </filter>
      </defs>
    </svg>
  `,
})
export class ColorBlindFiltersComponent {}
