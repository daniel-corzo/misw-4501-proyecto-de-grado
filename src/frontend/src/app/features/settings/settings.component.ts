import { Component, inject } from '@angular/core';
import { TranslocoPipe } from '@jsverse/transloco';
import { AccessibilityService, CbMode, FontSize } from '../../core/services/accessibility.service';

@Component({
  selector: 'app-settings',
  standalone: true,
  imports: [TranslocoPipe],
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
  styles: [`
    .settings {
      padding: 2rem;
      max-width: 600px;
      margin: 0 auto;
    }
    .settings__title {
      font: var(--font-h1);
      margin-bottom: var(--space-xl);
    }
    .settings__section {
      background: var(--color-white);
      border: 1px solid var(--color-border);
      border-radius: var(--border-radius);
      padding: var(--space-lg);
    }
    .settings__section-title {
      font: var(--font-h2-bold);
      margin-bottom: var(--space-sm);
    }
    .settings__section-desc {
      font: var(--font-body2);
      color: var(--color-text-muted);
      margin-bottom: var(--space-md);
    }
    .settings__subsection-title {
      font: var(--font-body2);
      font-weight: 600;
      color: var(--color-secondary);
      text-transform: uppercase;
      letter-spacing: 0.05em;
      margin-bottom: var(--space-sm);
    }
    .settings__subsection-title--mt {
      margin-top: var(--space-lg);
    }
    .settings__options {
      display: flex;
      gap: var(--space-sm);
      flex-wrap: wrap;
    }
    .settings__btn {
      padding: var(--space-sm) var(--space-md);
      border: 1px solid var(--color-border);
      border-radius: var(--border-radius);
      font: var(--font-body2);
      background: var(--color-bg);
      color: var(--color-text);
      cursor: pointer;
      transition: border-color 0.15s, color 0.15s, background 0.15s;
    }
    .settings__btn:hover {
      border-color: var(--color-primary);
      color: var(--color-primary);
    }
    .settings__btn--active {
      background: var(--color-primary);
      border-color: var(--color-primary);
      color: var(--color-white);
      font-weight: 600;
    }
  `],
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
