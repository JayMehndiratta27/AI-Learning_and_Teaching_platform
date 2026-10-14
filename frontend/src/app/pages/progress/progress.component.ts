import { CommonModule } from '@angular/common';
import { AfterViewInit, Component, ElementRef, ViewChild, inject } from '@angular/core';
import { Chart, registerables } from 'chart.js';
import { MatButtonToggleModule } from '@angular/material/button-toggle';
import { MatCardModule } from '@angular/material/card';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { LearningService } from '../../services/learning.service';

Chart.register(...registerables);

@Component({
  selector: 'app-progress',
  standalone: true,
  imports: [CommonModule, MatCardModule, MatButtonToggleModule, MatSnackBarModule],
  template: `
    <div class="flex flex-wrap items-center justify-between gap-3 mb-4">
      <h1 class="text-2xl font-bold">Progress & analytics</h1>
      <mat-button-toggle-group [value]="windowDays" (change)="setWindow($event.value)" aria-label="Time range">
        <mat-button-toggle [value]="7">7d</mat-button-toggle>
        <mat-button-toggle [value]="30">30d</mat-button-toggle>
        <mat-button-toggle [value]="90">90d</mat-button-toggle>
        <mat-button-toggle [value]="0">All</mat-button-toggle>
      </mat-button-toggle-group>
    </div>

    <div class="grid sm:grid-cols-2 lg:grid-cols-5 gap-3 mb-4">
      <mat-card class="p-3">
        <p class="text-xs text-slate-500 m-0">Total minutes</p>
        <p class="text-2xl font-bold m-0">{{ totals.minutes }}</p>
      </mat-card>
      <mat-card class="p-3">
        <p class="text-xs text-slate-500 m-0">Study days</p>
        <p class="text-2xl font-bold m-0">{{ totals.study_days }}</p>
      </mat-card>
      <mat-card class="p-3">
        <p class="text-xs text-slate-500 m-0">Avg minutes/day</p>
        <p class="text-2xl font-bold m-0">{{ totals.avg_minutes_per_day }}</p>
      </mat-card>
      <mat-card class="p-3">
        <p class="text-xs text-slate-500 m-0">Quiz attempts</p>
        <p class="text-2xl font-bold m-0">{{ totals.quiz_attempts }}</p>
      </mat-card>
      <mat-card class="p-3">
        <p class="text-xs text-slate-500 m-0">Avg score</p>
        <p class="text-2xl font-bold m-0">{{ totals.avg_score_pct }}%</p>
      </mat-card>
    </div>

    <div class="grid lg:grid-cols-2 gap-4">
      <mat-card class="p-4">
        <h2 class="font-semibold mb-2">Daily minutes</h2>
        <canvas #daily></canvas>
      </mat-card>
      <mat-card class="p-4">
        <h2 class="font-semibold mb-2">Subject time</h2>
        <canvas #subjects></canvas>
      </mat-card>
      <mat-card class="p-4 lg:col-span-2">
        <h2 class="font-semibold mb-2">Quiz scores trend</h2>
        <canvas #scores></canvas>
      </mat-card>
    </div>
  `,
})
export class ProgressComponent implements AfterViewInit {
  private readonly learning = inject(LearningService);
  private readonly snack = inject(MatSnackBar);
  @ViewChild('daily') daily?: ElementRef<HTMLCanvasElement>;
  @ViewChild('subjects') subjects?: ElementRef<HTMLCanvasElement>;
  @ViewChild('scores') scores?: ElementRef<HTMLCanvasElement>;
  private dailyChart?: Chart;
  private subjectsChart?: Chart;
  private scoresChart?: Chart;

  windowDays = 30;
  totals = {
    minutes: 0,
    study_days: 0,
    avg_minutes_per_day: 0,
    avg_score_pct: 0,
    quiz_attempts: 0,
  };

  ngAfterViewInit(): void {
    this.load();
  }

  setWindow(days: number): void {
    this.windowDays = Number(days);
    this.load();
  }

  private load(): void {
    this.learning.analyticsMe(this.windowDays).subscribe({
      next: (raw: any) => this.render(raw || {}),
      error: () => this.snack.open('Could not load analytics right now.', 'OK', { duration: 3000 }),
    });
  }

  private render(raw: any): void {
    this.totals = {
      ...this.totals,
      ...(raw.totals || {}),
    };
    this.dailyChart?.destroy();
    this.subjectsChart?.destroy();
    this.scoresChart?.destroy();

    requestAnimationFrame(() => {
      if (!this.daily?.nativeElement || !this.subjects?.nativeElement || !this.scores?.nativeElement) {
        return;
      }
      const daily = raw.daily_minutes || {};
      const labels = Object.keys(daily).sort();
      const values = labels.map((k) => daily[k]);
      this.dailyChart = new Chart(this.daily.nativeElement, {
        type: 'bar',
        data: {
          labels: labels.length ? labels : ['No data yet'],
          datasets: [{ label: 'Minutes', data: labels.length ? values : [0], backgroundColor: '#6366f1' }],
        },
        options: { responsive: true, plugins: { legend: { display: false } } },
      });

      const sm = raw.subject_minutes || {};
      const sLabels = Object.keys(sm);
      const sValues = sLabels.map((k) => sm[k]);
      this.subjectsChart = new Chart(this.subjects.nativeElement, {
        type: 'pie',
        data: {
          labels: sLabels.length ? sLabels : ['No data'],
          datasets: [
            {
              data: sLabels.length ? sValues : [1],
              backgroundColor: ['#6366f1', '#8b5cf6', '#ec4899', '#22c55e', '#f97316', '#06b6d4', '#eab308'],
            },
          ],
        },
        options: { responsive: true },
      });

      const recent = (raw.recent_quiz_results || []).slice().reverse();
      this.scoresChart = new Chart(this.scores.nativeElement, {
        type: 'line',
        data: {
          labels: recent.length ? recent.map((_: any, i: number) => `Q${i + 1}`) : ['—'],
          datasets: [
            {
              label: 'Score %',
              data: recent.length ? recent.map((r: any) => r.score_pct) : [0],
              borderColor: '#8b5cf6',
              tension: 0.35,
              fill: true,
              backgroundColor: 'rgba(139,92,246,0.15)',
            },
          ],
        },
        options: { responsive: true, scales: { y: { min: 0, max: 100 } } },
      });
    });
  }
}
