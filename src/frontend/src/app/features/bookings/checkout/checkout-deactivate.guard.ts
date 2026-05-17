import { CanDeactivateFn } from '@angular/router';
import { CheckoutComponent } from './checkout.component';

export const checkoutDeactivateGuard: CanDeactivateFn<CheckoutComponent> = (
  component
) => component.canDeactivate();
