import { HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { AuthService } from '../services/auth.service';

/** Attaches Bearer token to API requests. */
export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const auth = inject(AuthService);
  const token = auth.token();
  if (!token || !req.url.includes('/api')) {
    return next(req);
  }
  const clone = req.clone({ setHeaders: { Authorization: `Bearer ${token}` } });
  return next(clone);
};
