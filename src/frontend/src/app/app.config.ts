import { ApplicationConfig, LOCALE_ID, provideZoneChangeDetection, isDevMode } from '@angular/core';
import { provideRouter, withInMemoryScrolling } from '@angular/router';
import { provideHttpClient, withInterceptors } from '@angular/common/http';
import { provideTransloco } from '@jsverse/transloco';

import { routes } from './app.routes';
import { authInterceptor } from './core/interceptors/auth.interceptor';
import { errorInterceptor } from './core/interceptors/error.interceptor';
import { languageInterceptor } from './core/interceptors/language.interceptor';
import { TranslocoHttpLoader } from './transloco-http.loader';

export function getDefaultLang(): string {
  if (typeof window === 'undefined') return 'es';
  const savedLang = localStorage.getItem('appLang');
  const browserLang = navigator.language.split('-')[0];
  const lang = savedLang ?? (['en', 'es'].includes(browserLang) ? browserLang : 'es');
  if (typeof document !== 'undefined') {
    document.documentElement.lang = lang;
  }
  return lang;
}

export const appConfig: ApplicationConfig = {
  providers: [
    provideZoneChangeDetection({ eventCoalescing: true }),
    provideRouter(routes, withInMemoryScrolling({ scrollPositionRestoration: 'top' })),
    provideHttpClient(withInterceptors([authInterceptor, errorInterceptor, languageInterceptor])),
    provideTransloco({
      config: {
        availableLangs: ['es', 'en'],
        defaultLang: getDefaultLang(),
        fallbackLang: 'es',
        reRenderOnLangChange: true,
        prodMode: !isDevMode(),
      },
      loader: TranslocoHttpLoader
    }),
    { provide: LOCALE_ID, useValue: 'es-CO' },
  ],
};
