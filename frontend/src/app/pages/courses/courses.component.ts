import { CommonModule } from '@angular/common';
import { Component, OnInit, inject } from '@angular/core';
import { RouterLink } from '@angular/router';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { LearningService } from '../../services/learning.service';

@Component({
  selector: 'app-courses',
  standalone: true,
  imports: [CommonModule, RouterLink, MatCardModule, MatButtonModule],
  template: `
    <h1 class="text-2xl font-display font-bold mb-4">Learning modules</h1>
    <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
      @for (c of courses; track $any(c)._id) {
        <mat-card class="p-4 hover:-translate-y-0.5 transition lf-glass-card">
          <h2 class="font-semibold text-lg">{{ $any(c).title }}</h2>
          <p class="text-sm text-slate-600 dark:text-slate-300 line-clamp-3">{{ $any(c).description }}</p>
          <a mat-stroked-button class="mt-3" [routerLink]="['/courses', $any(c)._id]">Open</a>
        </mat-card>
      }
    </div>
  `,
})
export class CoursesComponent implements OnInit {
  private readonly learning = inject(LearningService);
  courses: unknown[] = [];

  ngOnInit(): void {
    this.learning.courses().subscribe((c) => (this.courses = c));
  }
}
