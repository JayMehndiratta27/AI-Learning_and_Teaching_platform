import { HttpErrorResponse } from '@angular/common/http';
import { Component, inject } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { AuthService } from '../../core/services/auth.service';
import { formatApiError } from '../../shared/format-http-error';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [
    ReactiveFormsModule,
    RouterLink,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatSnackBarModule,
  ],
  template: `
    <div
      class="lf-auth-page min-h-screen flex items-center justify-center px-4 py-12 bg-gradient-to-br from-slate-100 via-indigo-50 to-violet-100 dark:from-slate-950 dark:via-slate-900 dark:to-indigo-950"
    >
      <div class="w-full max-w-md">
        <div class="text-center mb-8">
          <p class="font-display text-sm font-semibold tracking-wide text-indigo-600 dark:text-indigo-300 uppercase">
            LearnFlow
          </p>
          <h1 class="mt-1 text-3xl font-display font-bold text-slate-900 dark:text-white">Welcome back</h1>
          <p class="mt-2 text-sm text-slate-600 dark:text-slate-400">Log in with the email and password you used at signup.</p>
        </div>
        <mat-card class="p-8 shadow-xl border border-slate-200/80 dark:border-slate-700/80 bg-white/95 dark:bg-slate-900/95 backdrop-blur-sm rounded-2xl">
          <form [formGroup]="form" (ngSubmit)="submit()" class="flex flex-col gap-1">
            <mat-form-field appearance="outline" class="w-full">
              <mat-label>Email</mat-label>
              <input matInput type="email" formControlName="email" autocomplete="username" />
            </mat-form-field>
            <mat-form-field appearance="outline" class="w-full">
              <mat-label>Password</mat-label>
              <input matInput type="password" formControlName="password" autocomplete="current-password" />
            </mat-form-field>
            <button
              mat-flat-button
              color="primary"
              class="w-full !py-2 !text-base mt-2 rounded-lg"
              [disabled]="form.invalid || loading"
            >
              {{ loading ? 'Signing in…' : 'Log in' }}
            </button>
          </form>
          <div class="mt-6 flex flex-wrap justify-between gap-2 text-sm">
            <a routerLink="/forgot-password" class="text-indigo-600 dark:text-indigo-400 hover:underline">Forgot password?</a>
            <a routerLink="/signup" class="text-indigo-600 dark:text-indigo-400 hover:underline">Create account</a>
          </div>
        </mat-card>
      </div>
    </div>
  `,
})
export class LoginComponent {
  private readonly fb = inject(FormBuilder);
  private readonly auth = inject(AuthService);
  private readonly router = inject(Router);
  private readonly snack = inject(MatSnackBar);

  loading = false;
  form = this.fb.nonNullable.group({
    email: ['', [Validators.required, Validators.email]],
    password: ['', [Validators.required, Validators.minLength(6)]],
  });

  submit(): void {
    if (this.form.invalid) return;
    this.loading = true;
    const { email, password } = this.form.getRawValue();
    this.auth.login(email, password).subscribe({
      next: () => {
        this.loading = false;
        void this.router.navigate(['/dashboard']);
      },
      error: (err: HttpErrorResponse) => {
        this.loading = false;
        this.snack.open(formatApiError(err, 'Login failed'), 'Dismiss', { duration: 8000 });
      },
    });
  }
}
