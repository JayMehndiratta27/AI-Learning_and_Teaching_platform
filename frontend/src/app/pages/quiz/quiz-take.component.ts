import { CommonModule } from '@angular/common';
import { Component, OnDestroy, OnInit, inject } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatRadioModule } from '@angular/material/radio';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { LearningService } from '../../services/learning.service';

@Component({
  selector: 'app-quiz-take',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    RouterLink,
    MatCardModule,
    MatButtonModule,
    MatRadioModule,
    MatFormFieldModule,
    MatInputModule,
    MatProgressBarModule,
    MatSnackBarModule,
    MatExpansionModule,
  ],
  template: `
    @if (quiz; as q) {
      <div class="flex justify-between items-center mb-2 flex-wrap gap-2">
        <h1 class="text-xl font-bold">{{ q.title }}</h1>
        <p class="font-mono">{{ format(timeLeft) }}</p>
      </div>
      <mat-progress-bar mode="determinate" [value]="progress"></mat-progress-bar>
      <div class="mt-4 space-y-4">
        @for (question of q.questions; track question.id; let idx = $index) {
          <mat-card class="p-4">
            <p class="text-sm text-slate-500 mb-1">Q{{ idx + 1 }} · {{ question.type }}</p>
            <p class="font-medium mb-3">{{ question.prompt }}</p>
            @if (question.type === 'mcq' || question.type === 'true_false') {
              <mat-radio-group [(ngModel)]="answers[question.id]" class="flex flex-col gap-1">
                @for (opt of question.options; track opt) {
                  <mat-radio-button [value]="opt">{{ opt }}</mat-radio-button>
                }
              </mat-radio-group>
            } @else {
              <mat-form-field class="w-full" appearance="outline">
                <mat-label>Your answer</mat-label>
                <input matInput [(ngModel)]="answers[question.id]" />
              </mat-form-field>
            }
          </mat-card>
        }
      </div>
      <div class="mt-4 flex flex-wrap gap-2">
        <button mat-flat-button color="primary" (click)="submit()" [disabled]="submitted || !allAnswered()">
          Submit answers
        </button>
        @if (submitted && result) {
          <button mat-stroked-button (click)="retake()">Retake quiz</button>
          <a mat-stroked-button routerLink="/quizzes">Back to list</a>
        }
      </div>
      @if (!allAnswered() && !submitted) {
        <p class="text-xs text-amber-700 dark:text-amber-300 mt-2">Answer every question before submitting.</p>
      }
      @if (result; as r) {
        <mat-card class="p-4 mt-4 border border-indigo-200/60 dark:border-indigo-900/60">
          <h2 class="font-semibold mb-2 text-lg">Results</h2>
          <p class="text-lg">
            Score <strong>{{ r['score_pct'] }}%</strong> ({{ r['correct'] }}/{{ r['total'] }})
          </p>
          <p class="text-sm mt-2 whitespace-pre-wrap text-slate-700 dark:text-slate-300">{{ r['ai_feedback'] }}</p>
          <p class="text-xs text-slate-500 mt-2">XP gained: {{ r['xp_gained'] }}</p>

          @if (r['details']?.length) {
            <mat-accordion class="mt-4 block">
              <mat-expansion-panel>
                <mat-expansion-panel-header>
                  <mat-panel-title>Review all answers</mat-panel-title>
                  <mat-panel-description>{{ r['correct'] }} correct · {{ r['total'] - r['correct'] }} to improve</mat-panel-description>
                </mat-expansion-panel-header>
                @for (row of r['details']; track row.question_id) {
                  <div
                    class="py-3 border-b border-slate-100 dark:border-slate-800 last:border-0 text-sm"
                    [class.opacity-80]="!row.correct"
                  >
                    <p class="font-medium">
                      {{ row.correct ? '✓' : '✗' }}
                      Q{{ $index + 1 }}
                    </p>
                    <p class="text-slate-600 dark:text-slate-400 mt-1">Yours: {{ row.your_answer || '—' }}</p>
                    @if (!row.correct) {
                      <p class="text-emerald-700 dark:text-emerald-400 mt-1">Expected: {{ row.expected }}</p>
                      <a
                        mat-stroked-button
                        color="primary"
                        class="!mt-2"
                        [routerLink]="['/chat']"
                        [queryParams]="tutorParams(row, q)"
                      >
                        Explain in AI Tutor
                      </a>
                    }
                  </div>
                }
              </mat-expansion-panel>
            </mat-accordion>
          }

          @if (r['score_pct'] < 80) {
            <div class="mt-4 flex flex-wrap gap-2">
              <a mat-flat-button color="primary" routerLink="/chat" [queryParams]="{ q: wholeQuizTutorPrompt(q, r) }">
                Open AI Tutor — full review
              </a>
            </div>
          }
        </mat-card>
      }
    }
  `,
})
export class QuizTakeComponent implements OnInit, OnDestroy {
  private readonly route = inject(ActivatedRoute);
  private readonly learning = inject(LearningService);
  private readonly snack = inject(MatSnackBar);

  quiz: { title: string; quiz_id: string; questions: any[]; time_limit_minutes: number } | null = null;
  answers: Record<string, string> = {};
  timeLeft = 0;
  started = 0;
  timer?: ReturnType<typeof setInterval>;
  result: Record<string, any> | null = null;
  submitted = false;

  get progress(): number {
    if (!this.quiz) return 0;
    const answered = Object.keys(this.answers).filter((k) => this.answers[k]?.toString().trim()).length;
    return (answered / this.quiz.questions.length) * 100;
  }

  ngOnInit(): void {
    const id = this.route.snapshot.paramMap.get('quizId')!;
    this.learning.quiz(id).subscribe((q: any) => {
      this.quiz = q;
      this.startTimer();
    });
  }

  ngOnDestroy(): void {
    this.clearTimer();
  }

  allAnswered(): boolean {
    if (!this.quiz) return false;
    return this.quiz.questions.every((qq) => this.answers[qq.id]?.toString().trim());
  }

  startTimer(): void {
    this.clearTimer();
    if (!this.quiz) return;
    this.timeLeft = (this.quiz.time_limit_minutes || 10) * 60;
    this.started = Date.now();
    this.timer = setInterval(() => {
      this.timeLeft -= 1;
      if (this.timeLeft <= 0) {
        this.clearTimer();
        this.submit(true);
      }
    }, 1000);
  }

  clearTimer(): void {
    if (this.timer) {
      clearInterval(this.timer);
      this.timer = undefined;
    }
  }

  format(sec: number): string {
    const m = Math.floor(Math.max(sec, 0) / 60);
    const s = Math.max(sec, 0) % 60;
    return `${m}:${s.toString().padStart(2, '0')}`;
  }

  tutorParams(row: { question_id: string; your_answer: string; expected: string }, q: { questions: any[] }): { q: string } {
    const qq = q.questions.find((x) => x.id === row.question_id);
    const stem = qq?.prompt || row.question_id;
    const your = (row.your_answer || '').toString();
    const expected = (row.expected || '').toString();

    // Keep the deep-link URL short. Long query params can break navigation.
    const clean = (s: string) => s.replace(/\s+/g, ' ').trim();
    const text = `offline tutor quiz explain step-by-step. Question: ${clean(stem)}. Expected: ${clean(
      expected,
    )}. You: ${clean(your)}.`;
    return { q: this.clampPrompt(text, 700) };
  }

  wholeQuizTutorPrompt(q: { title: string; questions: any[] }, r: Record<string, any>): string {
    const wrong = (r['details'] as any[])?.filter((d) => !d.correct) || [];
    const clean = (s: string) => s.replace(/\s+/g, ' ').trim();
    const wrongItems = wrong
      .slice(0, 3)
      .map((d) => {
        const qq = q.questions.find((x) => x.id === d.question_id);
        return `${clean(qq?.prompt || d.question_id)} (exp: ${clean(d.expected || '')}; you: ${clean(d.your_answer || '')})`;
      })
      .join(' | ');
    const more = wrong.length > 3 ? ` | +${wrong.length - 3} more` : '';
    const text = `offline tutor quiz review. Quiz: ${clean(q.title)}. Score: ${r['score_pct']}%. Wrong: ${wrongItems}${more}`;
    return this.clampPrompt(text, 800);
  }

  private clampPrompt(text: string, maxLen: number): string {
    const oneLine = text.replace(/\s+/g, ' ').trim();
    if (oneLine.length <= maxLen) return oneLine;
    return oneLine.slice(0, Math.max(0, maxLen - 3)) + '...';
  }

  retake(): void {
    this.submitted = false;
    this.result = null;
    this.answers = {};
    this.startTimer();
  }

  submit(auto = false): void {
    if (!this.quiz || this.submitted) return;
    if (!this.allAnswered() && !auto) {
      this.snack.open('Answer every question first.', 'OK', { duration: 3000 });
      return;
    }
    this.submitted = true;
    this.clearTimer();
    const payload = {
      quiz_id: this.quiz.quiz_id,
      duration_seconds: Math.floor((Date.now() - this.started) / 1000),
      answers: this.quiz.questions.map((qq) => ({ question_id: qq.id, answer: this.answers[qq.id] || '' })),
    };
    this.learning.submitQuiz(payload).subscribe({
      next: (res) => {
        this.result = res as any;
        if (auto) this.snack.open('Time up — submitted', 'OK');
      },
      error: (e) => {
        this.submitted = false;
        this.startTimer();
        this.snack.open(e.error?.detail || 'Submit failed', 'OK');
      },
    });
  }
}
