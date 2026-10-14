import { HttpClient } from '@angular/common/http';
import { Injectable, computed, inject, signal } from '@angular/core';
import { Router } from '@angular/router';
import { Observable, tap } from 'rxjs';
import { environment } from '../../../environments/environment';

export type UserRole = 'student' | 'teacher' | 'admin';

export interface UserProfile {
  _id: string;
  email: string;
  full_name: string;
  role: UserRole;
  xp?: number;
  streak_days?: number;
  weak_subjects?: string[];
  notification_prefs?: Record<string, boolean>;
  avatar_url?: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly http = inject(HttpClient);
  private readonly router = inject(Router);

  /** JWT access token (persisted). */
  readonly token = signal<string | null>(localStorage.getItem('lf_token'));
  /** Current user profile from `/auth/me`. */
  readonly user = signal<UserProfile | null>(null);

  readonly isAuthenticated = computed(() => !!this.token());
  readonly role = computed(() => this.user()?.role ?? null);

  constructor() {
    if (this.token()) {
      this.refreshProfile().subscribe({ error: () => this.logout() });
    }
  }

  private authHeader() {
    const t = this.token();
    return t ? { Authorization: `Bearer ${t}` } : {};
  }

  refreshProfile(): Observable<UserProfile> {
    return this.http.get<UserProfile>(`${environment.apiUrl}/auth/me`).pipe(
      tap((u) => this.user.set(u)),
    );
  }

  login(email: string, password: string): Observable<TokenResponse> {
    return this.http
      .post<TokenResponse>(`${environment.apiUrl}/auth/login`, { email, password })
      .pipe(
        tap((res) => {
          this.persistToken(res.access_token);
          this.refreshProfile().subscribe();
        }),
      );
  }

  register(body: { email: string; password: string; full_name: string; role: UserRole }): Observable<TokenResponse> {
    return this.http.post<TokenResponse>(`${environment.apiUrl}/auth/register`, body).pipe(
      tap((res) => {
        this.persistToken(res.access_token);
        this.refreshProfile().subscribe();
      }),
    );
  }

  forgotPassword(email: string): Observable<{ message: string; reset_token?: string }> {
    return this.http.post<{ message: string; reset_token?: string }>(
      `${environment.apiUrl}/auth/forgot-password`,
      { email },
    );
  }

  resetPassword(token: string, new_password: string): Observable<{ message: string }> {
    return this.http.post<{ message: string }>(`${environment.apiUrl}/auth/reset-password`, {
      token,
      new_password,
    });
  }

  logout(): void {
    localStorage.removeItem('lf_token');
    this.token.set(null);
    this.user.set(null);
    void this.router.navigate(['/login']);
  }

  private persistToken(accessToken: string): void {
    localStorage.setItem('lf_token', accessToken);
    this.token.set(accessToken);
  }
}
