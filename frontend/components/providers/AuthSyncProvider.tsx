'use client';

import { useEffect, useRef } from 'react';
import { syncAccessTokenToFrontend } from '@/lib/api/client';

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ||
  process.env.NEXT_PUBLIC_API_URL ||
  (process.env.NODE_ENV === 'development' ? 'http://localhost:10000' : '');

/**
 * Au chargement, si l'utilisateur a une session (refresh_token) mais que le
 * access_token n'est pas sync sur le domaine frontend (prod cross-domain),
 * on fait un refresh proactif pour synchroniser le cookie.
 */
export function AuthSyncProvider({ children }: { children: React.ReactNode }) {
  const hasRun = useRef(false);

  useEffect(() => {
    if (hasRun.current || typeof window === 'undefined') return;
    // Uniquement en prod (cross-domain : backend et frontend sur domains différents)
    if (process.env.NODE_ENV !== 'production' || !API_BASE_URL) return;

    const refreshToken = localStorage.getItem('refresh_token');
    if (!refreshToken) return;

    hasRun.current = true;

    fetch(`${API_BASE_URL}/api/auth/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: refreshToken }),
      credentials: 'include',
    })
      .then((res) => (res.ok ? res.json() : null))
      .then((data) => {
        if (data?.access_token) {
          syncAccessTokenToFrontend(data.access_token);
        }
      })
      .catch(() => {});
  }, []);

  return <>{children}</>;
}
