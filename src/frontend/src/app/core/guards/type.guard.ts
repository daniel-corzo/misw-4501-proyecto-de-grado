import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { AuthService } from '../services/auth.service';

export function typeGuard(...allowedTypes: string[]): CanActivateFn {
  return () => {
    const auth = inject(AuthService);
    const router = inject(Router);

    const type = auth.getUserType();
    if (type && allowedTypes.includes(type)) {
      return true;
    }

    return router.createUrlTree(['/']);
  };
}
