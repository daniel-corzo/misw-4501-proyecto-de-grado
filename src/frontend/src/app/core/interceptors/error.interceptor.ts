import { HttpInterceptorFn, HttpErrorResponse } from '@angular/common/http';
import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { catchError, throwError } from 'rxjs';
import { AuthService } from '../services/auth.service';
import { ToastService } from '../services/toast.service';

export const errorInterceptor: HttpInterceptorFn = (req, next) => {
  const auth = inject(AuthService);
  const router = inject(Router);
  const toast = inject(ToastService);

  return next(req).pipe(
    catchError((error: HttpErrorResponse) => {
      if (error.status === 401 && !req.url.includes('/auth/login')) {
        auth.clearSession();
        router.navigate(['/']).then(() => auth.openLoginModal());
      } else if (error.status === 403) {
        toast.warning('No tienes permisos para realizar esta acción');
      } else if (error.status >= 500) {
        toast.danger('Error del servidor, intenta más tarde');
      } else if (error.status === 0) {
        toast.danger('Sin conexión al servidor');
      }
      return throwError(() => error);
    })
  );
};
