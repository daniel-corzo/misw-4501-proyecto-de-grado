import { Component, inject } from '@angular/core';
import { TranslocoPipe } from '@jsverse/transloco';
import { AccessibilityService, CbMode, FontSize } from '../../core/services/accessibility.service';

@Component({
  selector: 'app-settings',
  standalone: true,
  imports: [TranslocoPipe],
  styleUrl: './settings.component.scss',
  template: `
    <div class="settings">
      <h1 class="settings__title">{{ 'settings.title' | transloco }}</h1>

      <section class="settings__section">
        <h2 class="settings__section-title">{{ 'accessibility.title' | transloco }}</h2>
        <p class="settings__section-desc">{{ 'accessibility.description' | transloco }}</p>

        <h3 class="settings__subsection-title">{{ 'accessibility.colorBlindMode' | transloco }}</h3>
        <div class="settings__options">
          @for (opt of cbOptions; track opt.value) {
            <button
              class="settings__btn"
              [class.settings__btn--active]="a11y.mode() === opt.value"
              type="button"
              (click)="a11y.setMode(opt.value)">
              {{ opt.labelKey | transloco }}
            </button>
          }
        </div>

        <h3 class="settings__subsection-title settings__subsection-title--mt">{{ 'accessibility.fontSize' | transloco }}</h3>
        <div class="settings__options">
          @for (opt of fsOptions; track opt.value) {
            <button
              class="settings__btn"
              [class.settings__btn--active]="a11y.fontSize() === opt.value"
              type="button"
              (click)="a11y.setFontSize(opt.value)">
              {{ opt.label }}
            </button>
          }
        </div>
      </section>
    </div>
  `,
})
export class SettingsComponent {
  readonly a11y = inject(AccessibilityService);

  readonly cbOptions: { value: CbMode; labelKey: string }[] = [
    { value: 'off',          labelKey: 'accessibility.off' },
    { value: 'protanopia',   labelKey: 'accessibility.protanopia' },
    { value: 'deuteranopia', labelKey: 'accessibility.deuteranopia' },
    { value: 'tritanopia',   labelKey: 'accessibility.tritanopia' },
  ];

  readonly fsOptions: { value: FontSize; label: string }[] = [
    { value: 'normal', label: 'A' },
    { value: 'large',  label: 'AA' },
    { value: 'xlarge', label: 'AAA' },
  ];
}
