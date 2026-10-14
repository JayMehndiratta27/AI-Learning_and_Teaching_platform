import { CommonModule } from '@angular/common';
import { Component, OnInit, inject } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { environment } from '../../../environments/environment';
import { LearningService } from '../../services/learning.service';

@Component({
  selector: 'app-downloads',
  standalone: true,
  imports: [CommonModule, MatCardModule, MatButtonModule],
  template: `
    <h1 class="text-2xl font-bold mb-4">Download center</h1>
    <div class="grid md:grid-cols-2 gap-4">
      @for (m of materials; track $any(m).id) {
        <mat-card class="p-4 flex justify-between items-center gap-3">
          <div>
            <p class="text-xs text-slate-500">{{ $any(m).subject }}</p>
            <p class="font-semibold">{{ $any(m).title }}</p>
            <span class="text-xs px-2 py-1 rounded bg-slate-100 dark:bg-slate-800 mt-2 inline-block">{{ $any(m).type }}</span>
          </div>
          <div class="flex flex-col gap-2">
            <a mat-stroked-button [href]="fileUrl($any(m).file)" target="_blank" rel="noopener">Preview</a>
            <a mat-flat-button color="primary" [href]="fileUrl($any(m).file)" download>Download</a>
          </div>
        </mat-card>
      }
    </div>
  `,
})
export class DownloadsComponent implements OnInit {
  private readonly learning = inject(LearningService);
  materials: unknown[] = [];

  ngOnInit(): void {
    this.learning.materials().subscribe((m) => (this.materials = m));
  }

  fileUrl(path: string): string {
    return `${environment.assetBase}${path}`;
  }
}
