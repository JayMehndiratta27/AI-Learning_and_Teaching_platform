import { HttpErrorResponse } from '@angular/common/http';

/** Turns HttpClient / API errors into a single user-visible string. */
export function formatApiError(err: unknown, fallback: string): string {
  if (err instanceof HttpErrorResponse) {
    if (err.status === 0) {
      return 'Cannot reach the API. Start the backend (uvicorn on port 8000) and allow CORS for http://localhost:4200.';
    }
    const body = err.error as Record<string, unknown> | null;
    if (body && typeof body['detail'] === 'string') {
      return body['detail'] as string;
    }
    if (Array.isArray(body?.['detail'])) {
      return (body['detail'] as { msg?: string }[])
        .map((e) => e.msg || '')
        .filter(Boolean)
        .join(' · ');
    }
    if (body && typeof body['message'] === 'string') {
      return body['message'] as string;
    }
    return err.message || fallback;
  }
  return fallback;
}
