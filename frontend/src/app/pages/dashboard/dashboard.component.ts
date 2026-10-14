import { CommonModule } from '@angular/common';
import { Component, OnInit, inject } from '@angular/core';
import { RouterLink } from '@angular/router';
import { forkJoin, of } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatChipsModule } from '@angular/material/chips';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { AuthService } from '../../core/services/auth.service';
import { LearningService } from '../../services/learning.service';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [
    CommonModule,
    RouterLink,
    MatCardModule,
    MatButtonModule,
    MatChipsModule,
    MatProgressBarModule,
    MatSnackBarModule,
  ],
  templateUrl: './dashboard.component.html',
})
export class DashboardComponent implements OnInit {
  private readonly learning = inject(LearningService);
  private readonly snack = inject(MatSnackBar);
  readonly auth = inject(AuthService);
  readonly Math = Math;

  recs: unknown[] = [];
  gamification: Record<string, unknown> | null = null;
  teacher: Record<string, unknown> | null = null;
  admin: Record<string, unknown> | null = null;
  users: unknown[] = [];

  ngOnInit(): void {
    forkJoin({
      recs: this.learning.recommendations().pipe(catchError(() => of({ items: [] }))),
      gamification: this.learning.gamification().pipe(catchError(() => of(null))),
    }).subscribe(({ recs, gamification }) => {
      this.recs = (recs as { items?: unknown[] }).items || [];
      this.gamification = gamification as Record<string, unknown> | null;
    });

    const role = this.auth.user()?.role;
    if (role === 'teacher' || role === 'admin') {
      this.learning
        .teacherOverview()
        .pipe(catchError(() => of(null)))
        .subscribe((t) => (this.teacher = t as Record<string, unknown> | null));
    }
    if (role === 'admin') {
      this.learning
        .adminStats()
        .pipe(catchError(() => of(null)))
        .subscribe((a) => (this.admin = a as Record<string, unknown> | null));
      this.learning
        .adminUsers()
        .pipe(catchError(() => of([])))
        .subscribe((u) => (this.users = u));
    }
  }

  completeChallenge(id: string): void {
    this.learning.completeChallenge(id).subscribe({
      next: () => {
        this.snack.open('Challenge completed — XP updated', 'OK', { duration: 3000 });
        this.learning.gamification().subscribe((g) => (this.gamification = g as Record<string, unknown>));
        this.auth.refreshProfile().subscribe();
      },
      error: () => this.snack.open('Could not complete challenge', 'OK'),
    });
  }
}
