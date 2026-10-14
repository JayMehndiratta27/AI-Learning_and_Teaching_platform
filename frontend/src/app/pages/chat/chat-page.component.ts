import { CommonModule } from '@angular/common';
import { Component, ElementRef, OnInit, ViewChild, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { ActivatedRoute } from '@angular/router';
import { distinctUntilChanged, filter, map, switchMap, tap } from 'rxjs';
import { ChatService } from '../../services/chat.service';
import { DomSanitizer, SafeHtml } from '@angular/platform-browser';

@Component({
  selector: 'app-chat-page',
  standalone: true,
  imports: [CommonModule, FormsModule, MatCardModule, MatButtonModule, MatFormFieldModule, MatInputModule, MatSnackBarModule],
  template: `
    <div class="max-w-3xl mx-auto flex flex-col gap-3 h-[calc(100vh-220px)]">
      <div class="flex justify-between items-center">
        <div class="flex items-center gap-3">
          <h1 class="text-2xl font-display font-bold">AI Tutor</h1>
          <span
            *ngIf="offlineMode"
            class="text-xs font-semibold px-2 py-1 rounded-full bg-indigo-50 dark:bg-indigo-900/50 text-indigo-800 dark:text-indigo-200 border border-indigo-200/70"
          >
            Offline Tutor
          </span>
        </div>
        <div class="flex gap-2">
          <button mat-stroked-button (click)="summarizeBlock()">AI summary</button>
          <button mat-stroked-button (click)="clear()">Clear chat</button>
        </div>
      </div>
      <div class="flex flex-wrap gap-2">
        <button mat-stroked-button type="button" *ngFor="let p of prompts; trackBy: trackByIndex" (click)="usePrompt(p)">
          {{ p }}
        </button>
      </div>
      <div #scrollBox class="flex-1 overflow-y-auto space-y-3 pr-1">
        <mat-card *ngIf="!messages.length && !typing" class="p-4 !shadow-none lf-glass-card dark:lf-glass-card">
          <p class="font-medium mb-1">Ask for help, step-by-step.</p>
          <p class="text-sm text-slate-600 dark:text-slate-300">
            Try a keyword like <span class="font-mono">deadlock</span>, <span class="font-mono">derivative</span>, or
            <span class="font-mono">Big-O</span>.
          </p>
        </mat-card>
        <div
          *ngFor="let m of messages; trackBy: trackByIndex"
          class="max-w-[90%] rounded-2xl px-3 py-2 text-sm whitespace-pre-wrap shadow-sm border transition hover:shadow-md"
          [class.ml-auto]="$any(m).role === 'user'"
          [class.bg-indigo-600]="$any(m).role === 'user'"
          [class.text-white]="$any(m).role === 'user'"
          [class.border-indigo-400]="$any(m).role === 'user'"
          [class.bg-slate-100]="$any(m).role !== 'user'"
          [class.border-slate-200]="$any(m).role !== 'user'"
          [class.dark:bg-slate-900]="$any(m).role !== 'user'"
          [class.dark:border-slate-800]="$any(m).role !== 'user'"
        >
          <div class="text-[11px] opacity-70 mb-1">{{ $any(m).role === 'user' ? 'You' : 'Tutor' }}</div>
          <div class="whitespace-pre-wrap" [innerHTML]="formatMessage($any(m).content)"></div>
          <div class="flex items-center justify-between gap-3 mt-2">
            <div class="text-[10px] opacity-70">{{ $any(m).created_at | date: 'shortTime' }}</div>
            <button
              *ngIf="$any(m).role !== 'user'"
              type="button"
              class="text-[10px] opacity-80 hover:opacity-100 underline underline-offset-2"
              (click)="copyMessage($any(m).content)"
            >
              Copy
            </button>
          </div>
        </div>

        <div *ngIf="typing" class="text-xs text-slate-500 flex items-center gap-2">
          <span class="inline-flex w-6 justify-between">
            <span class="animate-pulse">.</span>
            <span class="animate-pulse">.</span>
            <span class="animate-pulse">.</span>
          </span>
          Tutor is typing…
        </div>
      </div>
      <mat-form-field appearance="outline" class="w-full">
        <mat-label>Ask anything academic</mat-label>
        <textarea matInput rows="2" [(ngModel)]="draft" (keydown.enter)="$event.preventDefault(); send()"></textarea>
      </mat-form-field>
      <button mat-flat-button color="primary" (click)="send()" [disabled]="!draft.trim() || typing">Send</button>
    </div>
  `,
})
export class ChatPageComponent implements OnInit {
  private readonly chat = inject(ChatService);
  private readonly snack = inject(MatSnackBar);
  private readonly route = inject(ActivatedRoute);
  private readonly sanitizer = inject(DomSanitizer);
  @ViewChild('scrollBox') scrollBox?: ElementRef<HTMLDivElement>;

  messages: unknown[] = [];
  draft = '';
  typing = false;
  offlineMode = false;
  prompts = [
    'Explain Big-O with a simple array example',
    'Summarize virtual memory in 5 bullets',
    'Help me approach this quiz logically',
  ];

  ngOnInit(): void {
    this.chat
      .history()
      .pipe(
        tap((h) => (this.messages = h.messages || [])),
        switchMap(() =>
          this.route.queryParamMap.pipe(
            map((pm) => pm.get('q')?.trim() ?? ''),
            distinctUntilChanged(),
            filter((q) => q.length > 0),
          ),
        ),
      )
      .subscribe((q) => {
        this.draft = q;
        this.offlineMode = q.toLowerCase().includes('offline tutor');
        queueMicrotask(() => this.send());
      });
  }

  send(): void {
    if (this.typing) return;
    const text = this.draft.trim();
    if (!text) return;
    this.offlineMode = text.toLowerCase().includes('offline tutor');
    this.typing = true;
    this.draft = '';
    this.chat.send(text).subscribe({
      next: (res) => {
        this.messages = res.messages;
        this.typing = false;
        queueMicrotask(() => this.scrollBottom());
      },
      error: (e) => {
        this.typing = false;
        this.snack.open(e.error?.detail || 'Chat failed', 'OK');
      },
    });
  }

  usePrompt(p: string): void {
    this.draft = p;
    queueMicrotask(() => this.send());
  }

  copyMessage(content: string): void {
    try {
      navigator.clipboard?.writeText(content);
      this.snack.open('Copied', 'OK', { duration: 1200 });
    } catch {
      this.snack.open('Copy failed', 'OK', { duration: 1200 });
    }
  }

  summarizeBlock(): void {
    const text = this.draft.trim();
    if (text.length < 20) {
      this.snack.open('Enter at least 20 characters in the box below to summarize.', 'OK', { duration: 4000 });
      return;
    }
    this.chat.summarize(text).subscribe({
      next: (res) => {
        this.messages = [
          ...this.messages,
          { role: 'user', content: '[Summary request]', created_at: new Date().toISOString() },
          { role: 'assistant', content: res.summary, created_at: new Date().toISOString() },
        ];
        this.draft = '';
        queueMicrotask(() => this.scrollBottom());
      },
      error: (e) => this.snack.open(e.error?.detail || 'Summary failed', 'OK'),
    });
  }

  clear(): void {
    this.chat.clear().subscribe(() => (this.messages = []));
  }

  private scrollBottom(): void {
    const el = this.scrollBox?.nativeElement;
    if (el) el.scrollTop = el.scrollHeight;
  }

  trackByIndex(index: number): number {
    return index;
  }

  formatMessage(content: unknown): SafeHtml {
    const text = typeof content === 'string' ? content : String(content ?? '');
    return this.sanitizer.bypassSecurityTrustHtml(this.renderInlineAndBullets(text));
  }

  private escapeHtml(s: string): string {
    return s
      .replaceAll('&', '&amp;')
      .replaceAll('<', '&lt;')
      .replaceAll('>', '&gt;')
      .replaceAll('"', '&quot;')
      .replaceAll("'", '&#39;');
  }

  private renderInlineAndBullets(text: string): string {
    // 1) Split into lines and build paragraphs + lists from "- " bullets.
    const lines = text.replace(/\r\n/g, '\n').split('\n');
    const out: string[] = [];

    let inList = false;
    for (const rawLine of lines) {
      const line = rawLine ?? '';
      const trimmed = line.trim();

      if (/^\s*-\s+/.test(line)) {
        if (!inList) {
          out.push('<ul class="list-disc ml-5 mt-1 mb-1">');
          inList = true;
        }
        const item = line.replace(/^\s*-\s+/, '');
        out.push(`<li>${this.formatInline(item)}</li>`);
        continue;
      }

      if (trimmed.length === 0) {
        if (inList) {
          out.push('</ul>');
          inList = false;
        }
        continue;
      }

      if (inList) {
        out.push('</ul>');
        inList = false;
      }

      out.push(`<p class="m-0">${this.formatInline(line)}</p>`);
    }

    if (inList) out.push('</ul>');

    return out.join('');
  }

  private formatInline(s: string): string {
    // Tokenize URLs so '&' in query strings doesn't break href rendering after escaping.
    const urls: string[] = [];
    const urlTokenized = s.replace(/https?:\/\/[^\s<]+/g, (m) => {
      const idx = urls.push(m) - 1;
      return `[[URL${idx}]]`;
    });

    let escaped = this.escapeHtml(urlTokenized);

    // Convert markdown-ish bold/italic to tags (markers are removed).
    escaped = escaped.replace(/\*\*(.+?)\*\*/g, '<b>$1</b>');
    escaped = escaped.replace(/\*(.+?)\*/g, '<i>$1</i>');

    // Replace URL tokens with anchors.
    escaped = escaped.replace(/\[\[URL(\d+)\]\]/g, (_match, group1) => {
      const idx = Number(group1);
      const url = urls[idx] ?? '';
      const safeHref = this.escapeHtml(url);
      const safeText = this.escapeHtml(url);
      return `<a href="${safeHref}" target="_blank" rel="noopener noreferrer" class="text-indigo-600 underline underline-offset-2 dark:text-indigo-300">${safeText}</a>`;
    });

    return escaped;
  }
}
