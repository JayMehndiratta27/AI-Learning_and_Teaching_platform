import { CommonModule } from '@angular/common';
import { Component, inject } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { AuthService } from '../../core/services/auth.service';

@Component({
  selector: 'app-forgot-password',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    RouterLink,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatSnackBarModule,
  ],
  template: `
    <div class="min-h-screen flex items-center justify-center px-4 bg-slate-50 dark:bg-slate-950">
      <mat-card class="w-full max-w-md p-6">
        <h1 class="text-xl font-bold mb-4">Forgot password</h1>
        <form [formGroup]="form" (ngSubmit)="submit()">
          <mat-form-field class="w-full" appearance="outline">
            <mat-label>Email</mat-label>
            <input matInput formControlName="email" />
          </mat-form-field>
          <button mat-flat-button color="primary" class="w-full" [disabled]="form.invalid">Send reset</button>
        </form>
        @if (token) {
          <p class="mt-4 text-xs break-all">Demo reset token: {{ token }}</p>
        }
        <a routerLink="/login" class="block mt-4 text-sm text-indigo-600">Back to login</a>
      </mat-card>
    </div>
  `,
})
export class ForgotPasswordComponent {
  private readonly fb = inject(FormBuilder);
  private readonly auth = inject(AuthService);
  private readonly snack = inject(MatSnackBar);

  token = '';
  form = this.fb.nonNullable.group({ email: ['', [Validators.required, Validators.email]] });

  submit(): void {
    this.auth.forgotPassword(this.form.value.email!).subscribe({
      next: (res) => {
        this.token = res.reset_token || '';
        this.snack.open(res.message, 'OK', { duration: 5000 });
      },
      error: () => this.snack.open('Request failed', 'OK'),
    });
  }
}
