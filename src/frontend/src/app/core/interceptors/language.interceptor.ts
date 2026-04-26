import { HttpInterceptorFn } from '@angular/common/http';

export const languageInterceptor: HttpInterceptorFn = (req, next) => {
  const currentLang =
    (typeof localStorage !== 'undefined' && localStorage.getItem('appLang')) ||
    (typeof navigator !== 'undefined' && navigator.language && navigator.language.slice(0, 2)) ||
    'es';

  const clonedRequest = req.clone({
    headers: req.headers.set('Accept-Language', currentLang)
  });

  return next(clonedRequest);
};