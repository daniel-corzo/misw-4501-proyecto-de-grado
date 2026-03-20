import { bootstrapApplication } from '@angular/platform-browser';
import { registerLocaleData } from '@angular/common';

// Register all supported country locales
import localeEsCO from '@angular/common/locales/es-CO';
import localeEsMX from '@angular/common/locales/es-MX';
import localeEsAR from '@angular/common/locales/es-AR';
import localeEsCL from '@angular/common/locales/es-CL';
import localeEsPE from '@angular/common/locales/es-PE';
import localeEsEC from '@angular/common/locales/es-EC';
import localeEnUS from '@angular/common/locales/en';

registerLocaleData(localeEsCO, 'es-CO');
registerLocaleData(localeEsMX, 'es-MX');
registerLocaleData(localeEsAR, 'es-AR');
registerLocaleData(localeEsCL, 'es-CL');
registerLocaleData(localeEsPE, 'es-PE');
registerLocaleData(localeEsEC, 'es-EC');
registerLocaleData(localeEnUS, 'en-US');

import { appConfig } from './app/app.config';
import { AppComponent } from './app/app.component';

bootstrapApplication(AppComponent, appConfig)
  .catch((err) => console.error(err));
