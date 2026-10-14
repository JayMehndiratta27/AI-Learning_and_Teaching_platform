import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

@Injectable({ providedIn: 'root' })
export class ChatService {
  private readonly http = inject(HttpClient);
  private readonly base = environment.apiUrl;

  send(message: string): Observable<{ reply: string; messages: unknown[] }> {
    return this.http.post<{ reply: string; messages: unknown[] }>(`${this.base}/chat`, { message });
  }

  history(): Observable<{ messages: unknown[] }> {
    return this.http.get<{ messages: unknown[] }>(`${this.base}/chat/history`);
  }

  clear(): Observable<unknown> {
    return this.http.delete(`${this.base}/chat/history`);
  }

  summarize(text: string): Observable<{ summary: string }> {
    return this.http.post<{ summary: string }>(`${this.base}/chat/summary`, { text });
  }
}
