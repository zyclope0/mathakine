/**
 * Cross-domain auth session: refresh via HttpOnly cookie, mirror access_token and CSRF on the frontend host.
 * Consumed by AuthSyncProvider (bootstrap), useAuth (login/logout), and api/client (401 retry, ensure cookie).
 */

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ||
  process.env.NEXT_PUBLIC_API_URL ||
  (process.env.NODE_ENV === "development" ? "http://localhost:10000" : "");

export function getApiBaseUrl(): string {
  if (
    process.env.NODE_ENV === "production" &&
    (!API_BASE_URL || API_BASE_URL.includes("localhost"))
  ) {
    throw new Error(
      "NEXT_PUBLIC_API_BASE_URL doit être défini en production et ne peut pas être localhost"
    );
  }
  return API_BASE_URL || "http://localhost:10000";
}

/** Raw backend base URL; empty in prod misconfig — used to skip bootstrap without throwing. */
export function getBackendUrlOrEmpty(): string {
  return API_BASE_URL;
}

export function syncCsrfTokenToFrontend(csrfToken: string): void {
  if (typeof document === "undefined") return;
  const isSecure = typeof window !== "undefined" && window.location.protocol === "https:";
  document.cookie = `csrf_token=${csrfToken}; Path=/; SameSite=Strict; Max-Age=3600${isSecure ? "; Secure" : ""}`;
}

export async function syncAccessTokenToFrontend(accessToken: string): Promise<void> {
  if (typeof window === "undefined") return;
  try {
    await fetch("/api/auth/sync-cookie", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ access_token: accessToken }),
      credentials: "include",
    });
  } catch {
    // Non bloquant
  }
}

export async function clearFrontendAuthSyncCookie(): Promise<void> {
  if (typeof window === "undefined") return;
  try {
    await fetch("/api/auth/sync-cookie", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ clear: true }),
      credentials: "include",
    });
  } catch {
    /* ignore */
  }
}

interface RefreshResponseBody {
  access_token?: string;
  csrf_token?: string;
}

let isRefreshing = false;
let refreshPromise: Promise<boolean> | null = null;

/**
 * POST /api/auth/refresh with credentials; mirrors tokens onto frontend cookies when present.
 * @param syncCsrfFromResponse - false on initial app bootstrap (historical); true on 401 retry / ensure cookie.
 * @param apiBaseOverride - bootstrap only: same raw base as legacy AuthSync (no prod throw if mis-set).
 */
export async function refreshSessionViaHttpOnlyCookie(options: {
  syncCsrfFromResponse: boolean;
  apiBaseOverride?: string;
}): Promise<boolean> {
  if (isRefreshing && refreshPromise) {
    return refreshPromise;
  }

  isRefreshing = true;
  refreshPromise = (async () => {
    try {
      const origin = options.apiBaseOverride ?? getApiBaseUrl();
      const response = await fetch(`${origin}/api/auth/refresh`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({}),
      });

      if (!response.ok) {
        return false;
      }

      try {
        const data = (await response.json()) as RefreshResponseBody;
        if (data.access_token) {
          await syncAccessTokenToFrontend(data.access_token);
        }
        if (options.syncCsrfFromResponse && data.csrf_token) {
          syncCsrfTokenToFrontend(data.csrf_token);
        }
      } catch {
        // Réponse non-JSON non critique
      }
      return true;
    } catch (error) {
      console.error("[API Client] Erreur lors du refresh du token:", error);
      return false;
    } finally {
      isRefreshing = false;
      refreshPromise = null;
    }
  })();

  return refreshPromise;
}
