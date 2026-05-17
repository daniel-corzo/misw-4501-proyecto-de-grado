import { Injectable, signal } from '@angular/core';

export type CbMode = 'off' | 'protanopia' | 'deuteranopia' | 'tritanopia';
export type FontSize = 'normal' | 'large' | 'xlarge';

const VALID_CB_MODES: CbMode[] = ['protanopia', 'deuteranopia', 'tritanopia'];
const VALID_FONT_SIZES: FontSize[] = ['large', 'xlarge'];

@Injectable({ providedIn: 'root' })
export class AccessibilityService {
  readonly mode = signal<CbMode>('off');
  readonly fontSize = signal<FontSize>('normal');

  constructor() {
    if (typeof window !== 'undefined') {
      const savedMode = localStorage.getItem('appColorBlindMode') as CbMode | null;
      if (savedMode && VALID_CB_MODES.includes(savedMode)) {
        this.mode.set(savedMode);
      }
      const savedSize = localStorage.getItem('appFontSize') as FontSize | null;
      if (savedSize && VALID_FONT_SIZES.includes(savedSize)) {
        this.fontSize.set(savedSize);
      }
    }
    this.applyColorClass();
    this.applyFontSizeClass();
  }

  setMode(mode: CbMode): void {
    this.mode.set(mode);
    if (typeof window !== 'undefined') {
      localStorage.setItem('appColorBlindMode', mode);
    }
    this.applyColorClass();
  }

  setFontSize(size: FontSize): void {
    this.fontSize.set(size);
    if (typeof window !== 'undefined') {
      localStorage.setItem('appFontSize', size);
    }
    this.applyFontSizeClass();
  }

  private applyColorClass(): void {
    if (typeof document === 'undefined') return;
    const el = document.documentElement;
    VALID_CB_MODES.forEach(m => el.classList.remove(`cb-${m}`));
    if (this.mode() !== 'off') {
      el.classList.add(`cb-${this.mode()}`);
    }
  }

  private applyFontSizeClass(): void {
    if (typeof document === 'undefined') return;
    const el = document.documentElement;
    VALID_FONT_SIZES.forEach(s => el.classList.remove(`fs-${s}`));
    if (this.fontSize() !== 'normal') {
      el.classList.add(`fs-${this.fontSize()}`);
    }
  }
}
