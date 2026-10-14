import { CommonModule } from '@angular/common';
import { Component, OnInit, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { DomSanitizer, SafeResourceUrl } from '@angular/platform-browser';
import { LearningService } from '../../services/learning.service';

@Component({
  selector: 'app-videos',
  standalone: true,
  imports: [CommonModule, FormsModule, MatCardModule, MatButtonModule, MatFormFieldModule, MatInputModule],
  template: `
    <h1 class="text-2xl font-display font-bold mb-4">Video learning</h1>
    <mat-form-field appearance="outline" class="w-full max-w-md mb-4">
      <mat-label>Search</mat-label>
      <input matInput [(ngModel)]="query" (ngModelChange)="apply()" />
    </mat-form-field>
    <div class="grid lg:grid-cols-3 gap-4">
      <div class="lg:col-span-2">
        @if (active) {
          <mat-card class="p-2">
            <div class="aspect-video w-full">
              <iframe
                class="w-full h-full rounded"
                [src]="embed(active.youtube_id)"
                title="YouTube player"
                allowfullscreen
              ></iframe>
            </div>
            <div class="p-3 flex flex-wrap gap-2 justify-between items-center">
              <div>
                <p class="font-semibold">{{ active.title }}</p>
                <p class="text-xs text-slate-500">{{ active.subject }}</p>
              </div>
              <div class="flex flex-wrap gap-2">
                <a
                  mat-stroked-button
                  [href]="youtubeWatchUrl(active.youtube_id)"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  Open on YouTube
                </a>
                <button mat-stroked-button (click)="markWatched(active)">Save to history</button>
              </div>
            </div>
          </mat-card>
        }
      </div>
      <div class="space-y-2">
        <h2 class="font-semibold">Catalog</h2>
        @for (v of filtered; track v.video_id) {
          <button
            class="w-full text-left p-3 rounded border border-slate-200 dark:border-slate-800 hover:bg-indigo-50 dark:hover:bg-slate-900"
            (click)="active = v"
          >
            <p class="font-medium">{{ v.title }}</p>
            <p class="text-xs text-slate-500">{{ v.subject }}</p>
          </button>
        }
        <h3 class="font-semibold mt-4">History</h3>
        @for (h of history; track $any(h)._id) {
          <p class="text-xs text-slate-600">{{ $any(h).title }} · {{ $any(h).watched_at | date: 'short' }}</p>
        }
      </div>
    </div>
  `,
})
export class VideosComponent implements OnInit {
  private readonly learning = inject(LearningService);
  private readonly sanitizer = inject(DomSanitizer);

  videos: Array<{ video_id: string; title: string; subject: string; youtube_id: string }> = [];
  filtered: typeof this.videos = [];
  history: unknown[] = [];
  active: (typeof this.videos)[number] | null = null;
  query = '';

  ngOnInit(): void {
    this.learning.videos().subscribe((v) => {
      this.videos = v as typeof this.videos;
      this.filtered = this.videos;
      this.active = this.videos[0] || null;
    });
    this.learning.watchHistory().subscribe((h) => (this.history = h));
  }

  apply(): void {
    const q = this.query.toLowerCase();
    this.filtered = this.videos.filter(
      (v) => v.title.toLowerCase().includes(q) || v.subject.toLowerCase().includes(q),
    );
  }

  embed(id: string): SafeResourceUrl {
    const url = `https://www.youtube-nocookie.com/embed/${encodeURIComponent(id)}?rel=0&modestbranding=1`;
    return this.sanitizer.bypassSecurityTrustResourceUrl(url);
  }

  youtubeWatchUrl(id: string): string {
    return `https://www.youtube.com/watch?v=${encodeURIComponent(id)}`;
  }

  markWatched(v: { video_id: string; title: string; subject: string; youtube_id: string }): void {
    this.learning
      .addWatchHistory({
        video_id: v.video_id,
        title: v.title,
        subject: v.subject,
        youtube_id: v.youtube_id,
      })
      .subscribe(() => this.learning.watchHistory().subscribe((h) => (this.history = h)));
  }
}
