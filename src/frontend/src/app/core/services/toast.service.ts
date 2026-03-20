import { Injectable, signal } from '@angular/core';

export type ToastType = 'success' | 'danger' | 'warning' | 'info';

export interface Toast {
  id: number;
  type: ToastType;
  message: string;
}

const DEFAULT_DURATION_MS = 4000;
let nextId = 0;

@Injectable({ providedIn: 'root' })
export class ToastService {
  readonly toasts = signal<Toast[]>([]);

  success(message: string, duration = DEFAULT_DURATION_MS): void {
    this.#add({ type: 'success', message }, duration);
  }

  danger(message: string, duration = DEFAULT_DURATION_MS): void {
    this.#add({ type: 'danger', message }, duration);
  }

  warning(message: string, duration = DEFAULT_DURATION_MS): void {
    this.#add({ type: 'warning', message }, duration);
  }

  info(message: string, duration = DEFAULT_DURATION_MS): void {
    this.#add({ type: 'info', message }, duration);
  }

  dismiss(id: number): void {
    this.toasts.update((list) => list.filter((t) => t.id !== id));
  }

  #add(partial: Omit<Toast, 'id'>, duration: number): void {
    const toast: Toast = { id: nextId++, ...partial };
    this.toasts.update((list) => [...list, toast]);
    setTimeout(() => this.dismiss(toast.id), duration);
  }
}
