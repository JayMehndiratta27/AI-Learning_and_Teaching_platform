import { CommonModule } from '@angular/common';
import { Component, OnInit, inject } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatDividerModule } from '@angular/material/divider';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { AuthService } from '../../core/services/auth.service';
import { ThemeService } from '../../core/services/theme.service';
import { LearningService } from '../../services/learning.service';

@Component({
  selector: 'app-settings',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatCardModule,
    MatDividerModule,
    MatFormFieldModule,
    MatIconModule,
    MatInputModule,
    MatButtonModule,
    MatSlideToggleModule,
    MatSnackBarModule,
  ],
  template: `
    <h1 class="text-2xl font-display font-bold mb-2">Settings</h1>
    <p class="text-sm text-slate-600 dark:text-slate-400 mb-6">Account, appearance, and notification defaults.</p>
    <div class="grid md:grid-cols-2 gap-4">
      <mat-card class="p-4">
        <div class="flex items-center gap-2 mb-1">
          <mat-icon class="text-indigo-600">person</mat-icon>
          <h2 class="font-semibold m-0">Profile</h2>
        </div>
        <mat-divider class="!my-3" />
        <form [formGroup]="profile" (ngSubmit)="saveProfile()" class="space-y-3">
          <mat-form-field class="w-full" appearance="outline">
            <mat-label>Full name</mat-label>
            <input matInput formControlName="full_name" autocomplete="name" />
          </mat-form-field>
          <mat-form-field class="w-full" appearance="outline">
            <mat-label>Avatar URL</mat-label>
            <input matInput formControlName="avatar_url" type="url" placeholder="https://…" />
          </mat-form-field>
          <button mat-flat-button color="primary" [disabled]="profile.invalid">Save profile</button>
        </form>
      </mat-card>
      <mat-card class="p-4">
        <div class="flex items-center gap-2 mb-1">
          <mat-icon class="text-indigo-600">lock</mat-icon>
          <h2 class="font-semibold m-0">Security</h2>
        </div>
        <mat-divider class="!my-3" />
        <form [formGroup]="security" (ngSubmit)="savePassword()" class="space-y-3">
          <mat-form-field class="w-full" appearance="outline">
            <mat-label>Current password</mat-label>
            <input matInput type="password" formControlName="current_password" autocomplete="current-password" />
          </mat-form-field>
          <mat-form-field class="w-full" appearance="outline">
            <mat-label>New password</mat-label>
            <input matInput type="password" formControlName="new_password" autocomplete="new-password" />
          </mat-form-field>
          <button mat-stroked-button color="primary" [disabled]="security.invalid">Update password</button>
        </form>
      </mat-card>
      <mat-card class="p-4 md:col-span-2">
        <div class="flex items-center gap-2 mb-1">
          <mat-icon class="text-indigo-600">palette</mat-icon>
          <h2 class="font-semibold m-0">Appearance</h2>
        </div>
        <mat-divider class="!my-3" />
        <p class="text-sm text-slate-600 dark:text-slate-400 m-0 mb-3">
          Light and dark themes apply across the app. “System” follows your OS setting and updates automatically.
        </p>
        <div class="flex flex-wrap gap-2 items-center">
          @if (theme.preference() === 'light') {
            <button mat-flat-button color="primary" type="button" (click)="theme.set('light')">
              <mat-icon class="!align-middle mr-1">light_mode</mat-icon>
              Light
            </button>
          } @else {
            <button mat-stroked-button type="button" (click)="theme.set('light')">
              <mat-icon class="!align-middle mr-1">light_mode</mat-icon>
              Light
            </button>
          }
          @if (theme.preference() === 'dark') {
            <button mat-flat-button color="primary" type="button" (click)="theme.set('dark')">
              <mat-icon class="!align-middle mr-1">dark_mode</mat-icon>
              Dark
            </button>
          } @else {
            <button mat-stroked-button type="button" (click)="theme.set('dark')">
              <mat-icon class="!align-middle mr-1">dark_mode</mat-icon>
              Dark
            </button>
          }
          @if (theme.preference() === 'system') {
            <button mat-flat-button color="primary" type="button" (click)="theme.set('system')">
              <mat-icon class="!align-middle mr-1">brightness_auto</mat-icon>
              System
            </button>
          } @else {
            <button mat-stroked-button type="button" (click)="theme.set('system')">
              <mat-icon class="!align-middle mr-1">brightness_auto</mat-icon>
              System
            </button>
          }
          <span class="text-xs text-slate-500 ml-2">Active: {{ theme.mode() === 'dark' ? 'Dark' : 'Light' }}</span>
        </div>
      </mat-card>
      <mat-card class="p-4 md:col-span-2">
        <div class="flex items-center gap-2 mb-1">
          <mat-icon class="text-indigo-600">notifications</mat-icon>
          <h2 class="font-semibold m-0">Notifications</h2>
        </div>
        <mat-divider class="!my-3" />
        <form [formGroup]="prefs" (ngSubmit)="savePrefs()" class="space-y-3 max-w-xl">
          <mat-slide-toggle formControlName="quiz_reminders">Quiz reminders</mat-slide-toggle>
          <mat-slide-toggle formControlName="new_uploads">New uploads</mat-slide-toggle>
          <mat-slide-toggle formControlName="ai_recommendations">AI recommendations</mat-slide-toggle>
          <mat-slide-toggle formControlName="milestones">Milestones</mat-slide-toggle>
          <button mat-flat-button color="primary" type="submit" class="mt-2">Save preferences</button>
        </form>
      </mat-card>
    </div>
  `,
})
export class SettingsComponent implements OnInit {
  private readonly fb = inject(FormBuilder);
  private readonly learning = inject(LearningService);
  private readonly auth = inject(AuthService);
  private readonly snack = inject(MatSnackBar);
  readonly theme = inject(ThemeService);

  profile = this.fb.nonNullable.group({
    full_name: ['', Validators.required],
    avatar_url: [''],
  });
  security = this.fb.nonNullable.group({
    current_password: ['', Validators.required],
    new_password: ['', [Validators.required, Validators.minLength(6)]],
  });
  prefs = this.fb.nonNullable.group({
    quiz_reminders: true,
    new_uploads: true,
    ai_recommendations: true,
    milestones: true,
  });

  ngOnInit(): void {
    const u = this.auth.user();
    if (u) {
      this.profile.patchValue({ full_name: u.full_name, avatar_url: u.avatar_url || '' });
      const p = u.notification_prefs || {};
      this.prefs.patchValue({
        quiz_reminders: p['quiz_reminders'] ?? true,
        new_uploads: p['new_uploads'] ?? true,
        ai_recommendations: p['ai_recommendations'] ?? true,
        milestones: p['milestones'] ?? true,
      });
    }
  }

  saveProfile(): void {
    this.learning.updateProfile(this.profile.getRawValue()).subscribe({
      next: () => {
        this.snack.open('Profile saved', 'OK');
        this.auth.refreshProfile().subscribe();
      },
      error: () => this.snack.open('Failed', 'OK'),
    });
  }

  savePassword(): void {
    const v = this.security.getRawValue();
    this.learning.changePassword(v.current_password, v.new_password).subscribe({
      next: () => this.snack.open('Password updated', 'OK'),
      error: () => this.snack.open('Failed', 'OK'),
    });
  }

  savePrefs(): void {
    this.learning.updateSettings(this.prefs.getRawValue()).subscribe({
      next: () => this.snack.open('Preferences saved', 'OK'),
      error: () => this.snack.open('Failed', 'OK'),
    });
  }
}
