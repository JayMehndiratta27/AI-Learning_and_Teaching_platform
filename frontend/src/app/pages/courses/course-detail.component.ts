import { CommonModule } from '@angular/common';
import { Component, OnInit, inject } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { MatIconModule } from '@angular/material/icon';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { environment } from '../../../environments/environment';
import { LearningService } from '../../services/learning.service';
import { PdfPreviewDialogComponent } from './pdf-preview-dialog.component';

@Component({
  selector: 'app-course-detail',
  standalone: true,
  imports: [CommonModule, MatCardModule, MatButtonModule, MatIconModule, MatDialogModule, MatSnackBarModule],
  template: `
    @if (course; as c) {
      <div class="flex items-center justify-between mb-4">
        <div>
          <p class="text-xs uppercase text-slate-500">Subject pathway</p>
          <h1 class="text-2xl font-display font-bold">{{ $any(c).title }}</h1>
        </div>
        <button mat-stroked-button (click)="logStudy()">Log 15m study</button>
      </div>
      <div class="grid md:grid-cols-2 gap-4">
        @for (mod of $any(c).modules; track mod.id) {
          <mat-card class="p-4">
            <h2 class="font-semibold mb-2">{{ mod.title }}</h2>
            <div class="flex flex-wrap gap-2">
              @for (pdf of mod.pdfs; track pdf.id) {
                <button mat-stroked-button (click)="openPdf(pdf)">
                  <mat-icon>picture_as_pdf</mat-icon>
                  {{ pdf.title }}
                </button>
                <button mat-icon-button (click)="bookmark(pdf.id)" aria-label="Bookmark">
                  <mat-icon>bookmark_add</mat-icon>
                </button>
              }
            </div>
            <p class="text-xs text-slate-500 mt-2">Includes notes, videos, quizzes — use Downloads for bulk access.</p>
          </mat-card>
        }
      </div>
    }
  `,
})
export class CourseDetailComponent implements OnInit {
  private readonly route = inject(ActivatedRoute);
  private readonly learning = inject(LearningService);
  private readonly dialog = inject(MatDialog);
  private readonly snack = inject(MatSnackBar);

  course: unknown | null = null;

  ngOnInit(): void {
    const id = this.route.snapshot.paramMap.get('id')!;
    this.learning.course(id).subscribe((c) => (this.course = c));
  }

  openPdf(pdf: { file: string; title: string }): void {
    const url = `${environment.assetBase}${pdf.file}`;
    this.dialog.open(PdfPreviewDialogComponent, { data: { url, title: pdf.title }, width: '900px' });
  }

  bookmark(id: string): void {
    this.learning.addBookmark(id).subscribe({
      next: () => this.snack.open('Bookmarked', 'OK', { duration: 2000 }),
      error: () => this.snack.open('Failed', 'OK'),
    });
  }

  logStudy(): void {
    const subject = (this.course as { title?: string })?.title || 'General';
    this.learning.logProgress(subject, 15).subscribe({
      next: () => this.snack.open('Progress logged (+streak)', 'OK'),
      error: () => this.snack.open('Failed', 'OK'),
    });
  }
}
