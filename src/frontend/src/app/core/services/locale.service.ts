import { Injectable, signal, computed } from '@angular/core';

export type CountryCode = 'CO' | 'MX' | 'AR' | 'CL' | 'PE' | 'EC';

interface CountryConfig {
  locale: string;
  currency: string;
  currencyDisplay: string;
  name: string;
  /** Decimal digits for currency formatting (CLP has 0) */
  currencyDigits: string;
}

export const COUNTRY_CONFIG: Record<CountryCode, CountryConfig> = {
  CO: { locale: 'es-CO', currency: 'COP', currencyDisplay: '$',  name: 'Colombia',  currencyDigits: '1.0-0' },
  MX: { locale: 'es-MX', currency: 'MXN', currencyDisplay: '$',  name: 'México',    currencyDigits: '1.2-2' },
  AR: { locale: 'es-AR', currency: 'ARS', currencyDisplay: '$',  name: 'Argentina', currencyDigits: '1.2-2' },
  CL: { locale: 'es-CL', currency: 'CLP', currencyDisplay: '$',  name: 'Chile',     currencyDigits: '1.0-0' },
  PE: { locale: 'es-PE', currency: 'PEN', currencyDisplay: 'S/', name: 'Perú',      currencyDigits: '1.2-2' },
  EC: { locale: 'es-EC', currency: 'USD', currencyDisplay: '$',  name: 'Ecuador',   currencyDigits: '1.2-2' },
};

const STORAGE_KEY = 'th_country';
const DEFAULT_COUNTRY: CountryCode = 'CO';

@Injectable({ providedIn: 'root' })
export class LocaleService {
  private readonly _country = signal<CountryCode>(this.#readSaved());

  /** Active country code (e.g. 'CO') */
  readonly country = this._country.asReadonly();

  /** Active locale string (e.g. 'es-CO') — fed into Angular pipes */
  readonly locale = computed(() => COUNTRY_CONFIG[this._country()].locale);

  /** Active ISO 4217 currency code (e.g. 'COP') */
  readonly currencyCode = computed(() => COUNTRY_CONFIG[this._country()].currency);

  /** Digit-info string for CurrencyPipe (e.g. '1.0-0' for COP/CLP) */
  readonly currencyDigits = computed(() => COUNTRY_CONFIG[this._country()].currencyDigits);

  /** Full config for the active country */
  readonly config = computed(() => COUNTRY_CONFIG[this._country()]);

  /** All supported countries for a country picker UI */
  readonly supportedCountries = Object.entries(COUNTRY_CONFIG).map(
    ([code, cfg]) => ({ code: code as CountryCode, ...cfg })
  );

  setCountry(code: CountryCode): void {
    localStorage.setItem(STORAGE_KEY, code);
    this._country.set(code);
  }

  #readSaved(): CountryCode {
    const saved = localStorage.getItem(STORAGE_KEY) as CountryCode | null;
    return saved && saved in COUNTRY_CONFIG ? saved : DEFAULT_COUNTRY;
  }
}

/**
 * Factory used by LOCALE_ID provider in app.config.ts.
 * Reads from localStorage at bootstrap time so Angular's built-in pipes
 * receive the correct locale without needing an injected service.
 */
export function localeIdFactory(): string {
  const saved = localStorage.getItem(STORAGE_KEY) as CountryCode | null;
  const code = saved && saved in COUNTRY_CONFIG ? saved : DEFAULT_COUNTRY;
  return COUNTRY_CONFIG[code].locale;
}
