import { CommonModule } from '@angular/common';
import { Component, OnInit, inject } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { LearningService } from '../../services/learning.service';

@Component({
  selector: 'app-notifications',
  standalone: true,
  imports: [CommonModule, MatCardModule, MatButtonModule],
  template: `
    <h1 class="text-2xl font-bold mb-4">Notifications</h1>
    <div class="space-y-3">
      @for (n of items; track $any(n)._id) {
        <mat-card class="p-4 flex justify-between gap-3">
          <div>
            <p class="font-semibold">{{ $any(n).title }}</p>
            <p class="text-sm text-slate-600 dark:text-slate-300">{{ $any(n).body }}</p>
            <p class="text-xs text-slate-400 mt-1">{{ $any(n).created_at | date: 'medium' }}</p>
          </div>
          <button mat-stroked-button (click)="read($any(n)._id)" [disabled]="$any(n).read">
            {{ $any(n).read ? 'Read' : 'Mark read' }}
          </button>
        </mat-card>
      } @empty {
        <p class="text-sm text-slate-500">No notifications yet.</p>
      }
    </div>
  `,
})
export class NotificationsComponent implements OnInit {
  private readonly learning = inject(LearningService);
  items: unknown[] = [];

  ngOnInit(): void {
    this.load();
  }

  load(): void {
    this.learning.notifications().subscribe((n) => (this.items = n));
  }

  read(id: string): void {
    this.learning.markNotificationRead(id).subscribe(() => this.load());
  }
}
