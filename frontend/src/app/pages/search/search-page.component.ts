import { CommonModule } from '@angular/common';
import { Component, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatListModule } from '@angular/material/list';
import { LearningService } from '../../services/learning.service';

@Component({
  selector: 'app-search-page',
  standalone: true,
  imports: [CommonModule, FormsModule, MatCardModule, MatFormFieldModule, MatInputModule, MatButtonModule, MatListModule],
  template: `
    <h1 class="text-2xl font-bold mb-4">Global search</h1>
    <mat-card class="p-4 mb-4">
      <mat-form-field class="w-full" appearance="outline">
        <input matInput [(ngModel)]="q" (keyup.enter)="run()" placeholder="Search" />
      </mat-form-field>
      <button mat-flat-button color="primary" (click)="run()">Search</button>
    </mat-card>
    <mat-card>
      <mat-list>
        @for (r of results; track $index) {
          <mat-list-item>
            <span matListItemTitle>{{ $any(r).title }}</span>
            <span matListItemLine>{{ $any(r).type }}</span>
          </mat-list-item>
        } @empty {
          <p class="p-4 text-sm text-slate-500">Enter a query to see matches.</p>
        }
      </mat-list>
    </mat-card>
  `,
})
export class SearchPageComponent {
  private readonly learning = inject(LearningService);
  q = '';
  results: unknown[] = [];

  run(): void {
    if (!this.q.trim()) return;
    this.learning.search(this.q.trim()).subscribe((res) => (this.results = res.results));
  }
}
