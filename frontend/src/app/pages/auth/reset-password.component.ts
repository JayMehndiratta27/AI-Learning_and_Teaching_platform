import { CommonModule } from '@angular/common';
import { Component, inject } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { AuthService } from '../../core/services/auth.service';

@Component({
  selector: 'app-reset-password',
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
    <div class="min-h-screen flex items-center justify-center px-4">
      <mat-card class="w-full max-w-md p-6">
        <h1 class="text-xl font-bold mb-4">Reset password</h1>
        <form [formGroup]="form" (ngSubmit)="submit()">
          <mat-form-field class="w-full" appearance="outline">
            <mat-label>Reset token</mat-label>
            <input matInput formControlName="token" />
          </mat-form-field>
          <mat-form-field class="w-full" appearance="outline">
            <mat-label>New password</mat-label>
            <input matInput type="password" formControlName="new_password" />
          </mat-form-field>
          <button mat-flat-button color="primary" class="w-full" [disabled]="form.invalid">Update</button>
        </form>
        <a routerLink="/login" class="block mt-4 text-sm">Login</a>
      </mat-card>
    </div>
  `,
})
export class ResetPasswordComponent {
  private readonly fb = inject(FormBuilder);
  private readonly auth = inject(AuthService);
  private readonly router = inject(Router);
  private readonly snack = inject(MatSnackBar);

  form = this.fb.nonNullable.group({
    token: ['', Validators.required],
    new_password: ['', [Validators.required, Validators.minLength(6)]],
  });

  submit(): void {
    const v = this.form.getRawValue();
    this.auth.resetPassword(v.token, v.new_password).subscribe({
      next: () => {
        this.snack.open('Password updated — please login', 'OK');
        void this.router.navigate(['/login']);
      },
      error: (e) => this.snack.open(e.error?.detail || 'Failed', 'OK'),
    });
  }
}
