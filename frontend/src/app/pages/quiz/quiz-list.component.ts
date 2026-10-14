import { CommonModule } from '@angular/common';
import { Component, OnInit, inject } from '@angular/core';
import { RouterLink } from '@angular/router';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { LearningService } from '../../services/learning.service';

@Component({
  selector: 'app-quiz-list',
  standalone: true,
  imports: [CommonModule, RouterLink, MatCardModule, MatButtonModule],
  template: `
    <h1 class="text-2xl font-display font-bold mb-4">Quizzes</h1>
    <div class="grid md:grid-cols-2 gap-4">
      @for (q of quizzes; track $any(q).quiz_id) {
        <mat-card class="p-4 flex flex-col gap-2">
          <div>
            <p class="text-xs uppercase text-slate-500">{{ $any(q).subject }}</p>
            <h2 class="font-semibold text-lg">{{ $any(q).title }}</h2>
            <p class="text-sm text-slate-600">{{ $any(q).time_limit_minutes }} minutes</p>
          </div>
          <a mat-flat-button color="primary" [routerLink]="['/quizzes', $any(q).quiz_id]">Start</a>
        </mat-card>
      }
    </div>
    <mat-card class="p-4 mt-6">
      <h2 class="font-semibold mb-2">Leaderboard</h2>
      @for (row of board; track $index) {
        <div class="flex justify-between text-sm border-b border-slate-100 dark:border-slate-800 py-1">
          <span>{{ $any(row).user_label }}</span>
          <span>{{ $any(row).avg_score }}% ({{ $any(row).attempts }})</span>
        </div>
      }
    </mat-card>
  `,
})
export class QuizListComponent implements OnInit {
  private readonly learning = inject(LearningService);
  quizzes: unknown[] = [];
  board: unknown[] = [];

  ngOnInit(): void {
    this.learning.quizzes().subscribe((q) => (this.quizzes = q));
    this.learning.leaderboard().subscribe((b) => (this.board = b));
  }
}
