import { HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { TranslocoService } from '@jsverse/transloco';

export const languageInterceptor: HttpInterceptorFn = (req, next) => {
  const translocoService = inject(TranslocoService);
  const currentLang = translocoService.getActiveLang();

  const clonedRequest = req.clone({
    headers: req.headers.set('Accept-Language', currentLang)
  });

  return next(clonedRequest);
};