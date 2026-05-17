import { Component, inject } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { ToastComponent } from './shared/components/toast/toast.component';
import { ModalComponent } from './shared/components/modal/modal.component';
import { LoginComponent } from './features/auth/login/login.component';
import { RegisterComponent } from './features/auth/register/register.component';
import { AuthService } from './core/services/auth.service';
import { AccessibilityService } from './core/services/accessibility.service';
import { ColorBlindFiltersComponent } from './shared/components/color-blind-filters/color-blind-filters.component';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, ToastComponent, ModalComponent, LoginComponent, RegisterComponent, ColorBlindFiltersComponent],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss',
})
export class AppComponent {
  readonly auth = inject(AuthService);
  readonly accessibility = inject(AccessibilityService);
}
