import { DOCUMENT } from '@angular/common';
import { Injectable, computed, effect, inject, signal } from '@angular/core';

const STORAGE_KEY = 'learnflow_theme';

export type ThemePreference = 'light' | 'dark' | 'system';

function readPreference(): ThemePreference {
  const v = localStorage.getItem(STORAGE_KEY);
  if (v === 'light' || v === 'dark' || v === 'system') return v;
  return 'light';
}

@Injectable({ providedIn: 'root' })
export class ThemeService {
  private readonly doc = inject(DOCUMENT);
  private readonly systemDark = signal(
    typeof window !== 'undefined' &&
      window.matchMedia?.('(prefers-color-scheme: dark)')?.matches === true,
  );

  /** Stored choice: light, dark, or follow OS. */
  readonly preference = signal<ThemePreference>(readPreference());

  /** Resolved appearance for icons and `dark` class. */
  readonly mode = computed<'light' | 'dark'>(() => {
    const p = this.preference();
    if (p === 'system') return this.systemDark() ? 'dark' : 'light';
    return p;
  });

  constructor() {
    if (typeof window !== 'undefined') {
      const mq = window.matchMedia('(prefers-color-scheme: dark)');
      mq.addEventListener('change', (e) => this.systemDark.set(e.matches));
    }
    effect(() => {
      const m = this.mode();
      localStorage.setItem(STORAGE_KEY, this.preference());
      const root = this.doc.documentElement;
      root.classList.toggle('dark', m === 'dark');
      root.setAttribute('data-theme', m);
    });
  }

  toggle(): void {
    const cur = this.mode();
    this.preference.set(cur === 'dark' ? 'light' : 'dark');
  }

  set(mode: ThemePreference): void {
    this.preference.set(mode);
  }
}
