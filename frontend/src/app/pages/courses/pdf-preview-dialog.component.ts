import { Component, inject } from '@angular/core';
import { DomSanitizer, SafeResourceUrl } from '@angular/platform-browser';
import { MAT_DIALOG_DATA, MatDialogModule, MatDialogRef } from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';

@Component({
  selector: 'app-pdf-preview-dialog',
  standalone: true,
  imports: [MatDialogModule, MatButtonModule],
  template: `
    <h2 mat-dialog-title>{{ data.title }}</h2>
    <div mat-dialog-content class="h-[70vh]">
      <iframe [src]="safeUrl" class="w-full h-full border-0"></iframe>
    </div>
    <div mat-dialog-actions align="end">
      <a mat-button [href]="data.url" target="_blank" rel="noopener">Open in tab</a>
      <button mat-flat-button mat-dialog-close>Close</button>
    </div>
  `,
})
export class PdfPreviewDialogComponent {
  readonly data = inject<{ url: string; title: string }>(MAT_DIALOG_DATA);
  readonly ref = inject(MatDialogRef<PdfPreviewDialogComponent>);
  readonly safeUrl: SafeResourceUrl = inject(DomSanitizer).bypassSecurityTrustResourceUrl(this.data.url);
}
