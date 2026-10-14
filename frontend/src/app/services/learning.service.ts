import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

@Injectable({ providedIn: 'root' })
export class LearningService {
  private readonly http = inject(HttpClient);
  private readonly base = environment.apiUrl;

  courses(): Observable<unknown[]> {
    return this.http.get<unknown[]>(`${this.base}/courses`);
  }

  course(id: string): Observable<unknown> {
    return this.http.get<unknown>(`${this.base}/courses/${id}`);
  }

  materials(subject?: string): Observable<unknown[]> {
    let params = new HttpParams();
    if (subject) params = params.set('subject', subject);
    return this.http.get<unknown[]>(`${this.base}/materials`, { params });
  }

  bookmarks(): Observable<{ ids: string[] }> {
    return this.http.get<{ ids: string[] }>(`${this.base}/materials/bookmarks`);
  }

  addBookmark(materialId: string): Observable<unknown> {
    return this.http.post(`${this.base}/materials/bookmarks`, { material_id: materialId });
  }

  removeBookmark(materialId: string): Observable<unknown> {
    return this.http.delete(`${this.base}/materials/bookmarks/${materialId}`);
  }

  quizzes(subject?: string): Observable<unknown[]> {
    let params = new HttpParams();
    if (subject) params = params.set('subject', subject);
    return this.http.get<unknown[]>(`${this.base}/quizzes`, { params });
  }

  quiz(id: string): Observable<unknown> {
    return this.http.get<unknown>(`${this.base}/quizzes/${id}`);
  }

  submitQuiz(body: unknown): Observable<unknown> {
    return this.http.post(`${this.base}/quizzes/submit`, body);
  }

  leaderboard(): Observable<unknown[]> {
    return this.http.get<unknown[]>(`${this.base}/quizzes/leaderboard/summary`);
  }

  analyticsMe(days = 30): Observable<unknown> {
    const params = new HttpParams().set('days', String(days));
    return this.http.get(`${this.base}/analytics/me`, { params });
  }

  logProgress(subject: string, minutes: number, activityType = 'study'): Observable<unknown> {
    return this.http.post(`${this.base}/analytics/progress`, {
      subject,
      minutes,
      activity_type: activityType,
    });
  }

  recommendations(): Observable<{ items: unknown[] }> {
    return this.http.get<{ items: unknown[] }>(`${this.base}/recommendations`);
  }

  videos(subject?: string): Observable<unknown[]> {
    let params = new HttpParams();
    if (subject) params = params.set('subject', subject);
    return this.http.get<unknown[]>(`${this.base}/videos`, { params });
  }

  watchHistory(): Observable<unknown[]> {
    return this.http.get<unknown[]>(`${this.base}/videos/watch-history`);
  }

  addWatchHistory(body: Record<string, string>): Observable<unknown> {
    return this.http.post(`${this.base}/videos/watch-history`, body);
  }

  notifications(): Observable<unknown[]> {
    return this.http.get<unknown[]>(`${this.base}/notifications`);
  }

  markNotificationRead(id: string): Observable<unknown> {
    return this.http.patch(`${this.base}/notifications/${id}/read`, {});
  }

  search(q: string): Observable<{ results: unknown[] }> {
    const params = new HttpParams().set('q', q);
    return this.http.get<{ results: unknown[] }>(`${this.base}/search`, { params });
  }

  gamification(): Observable<unknown> {
    return this.http.get(`${this.base}/gamification/me`);
  }

  completeChallenge(challengeId: string): Observable<unknown> {
    return this.http.post(`${this.base}/gamification/challenges/complete`, { challenge_id: challengeId });
  }

  teacherOverview(): Observable<unknown> {
    return this.http.get(`${this.base}/teacher/overview`);
  }

  adminStats(): Observable<unknown> {
    return this.http.get(`${this.base}/admin/stats`);
  }

  adminUsers(): Observable<unknown[]> {
    return this.http.get<unknown[]>(`${this.base}/users/admin/list`);
  }

  updateProfile(body: { full_name?: string; avatar_url?: string }): Observable<unknown> {
    return this.http.patch(`${this.base}/users/me`, body);
  }

  changePassword(current_password: string, new_password: string): Observable<unknown> {
    return this.http.post(`${this.base}/users/me/password`, { current_password, new_password });
  }

  updateSettings(notification_prefs: Record<string, boolean>): Observable<unknown> {
    return this.http.patch(`${this.base}/users/me/settings`, { notification_prefs });
  }
}
