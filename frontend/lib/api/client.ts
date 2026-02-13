/**
 * Client API pour les requêtes vers le backend
 * Gère l'authentification via cookies HTTP-only avec refresh automatique
 */

// URL du backend API
// En développement: peut utiliser localhost par défaut
// En production: DOIT être définie via NEXT_PUBLIC_API_BASE_URL
const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ||
  process.env.NEXT_PUBLIC_API_URL ||
  (process.env.NODE_ENV === "development" ? "http://localhost:10000" : "");

function getApiBaseUrl(): string {
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

export interface ApiError {
  message: string;
  status: number;
  details?: unknown;
}

export class ApiClientError extends Error {
  status: number;
  details?: unknown;

  constructor(message: string, status: number, details?: unknown) {
    super(message);
    this.name = "ApiClientError";
    this.status = status;
    this.details = details;
  }
}

// État global pour gérer le refresh en cours
let isRefreshing = false;
let refreshPromise: Promise<boolean> | null = null;

/**
 * Récupère un token CSRF pour les actions sensibles (reset password, changement mot de passe, suppression compte).
 * Protège contre les attaques CSRF (audit 3.2).
 */
export async function getCsrfToken(): Promise<string> {
  const baseUrl = getApiBaseUrl();
  const res = await fetch(`${baseUrl}/api/auth/csrf`, {
    method: "GET",
    credentials: "include",
  });
  if (!res.ok) {
    throw new ApiClientError("Impossible de récupérer le token de sécurité", res.status);
  }
  const data = (await res.json()) as { csrf_token: string };
  if (!data?.csrf_token) {
    throw new ApiClientError("Token CSRF invalide", 0);
  }
  return data.csrf_token;
}

/**
 * Sync access_token sur le domaine frontend (pour prod cross-domain).
 * Exporté pour usage au chargement de l'app (utilisateurs revenant avec session).
 */
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

/**
 * S'assure que le cookie access_token est présent sur le domaine frontend.
 * En prod cross-domain : tente un refresh (cookie HttpOnly envoyé auto) puis sync.
 * À appeler avant toute requête qui transite par les routes API Next.js (proxy).
 */
export async function ensureFrontendAuthCookie(): Promise<void> {
  if (typeof window === "undefined") return;
  if (process.env.NODE_ENV !== "production") return; // En dev, même domaine
  await refreshAccessToken();
}

/**
 * Rafraîchit le token via le cookie refresh_token (HttpOnly).
 * Pas de body : le cookie est envoyé automatiquement avec credentials: 'include'.
 * Sécurité : refresh_token jamais exposé à JavaScript (pas de localStorage).
 */
async function refreshAccessToken(): Promise<boolean> {
  if (isRefreshing && refreshPromise) {
    return refreshPromise;
  }

  isRefreshing = true;
  refreshPromise = (async () => {
    try {
      const response = await fetch(`${getApiBaseUrl()}/api/auth/refresh`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include", // Cookie refresh_token (HttpOnly) envoyé automatiquement
        body: JSON.stringify({}), // Body vide ; le cookie suffit
      });

      if (response.ok) {
        try {
          const data = await response.json();
          if (data.access_token) {
            await syncAccessTokenToFrontend(data.access_token);
          }
        } catch {
          // Réponse non-JSON non critique
        }
        return true;
      }
      return false;
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

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
    let errorDetails: unknown;

    try {
      const errorData = await response.json();
      errorMessage = errorData.message || errorData.detail || errorData.error || errorMessage;
      errorDetails = errorData;
    } catch {
      // Si la réponse n'est pas du JSON, utiliser le texte
      try {
        errorMessage = await response.text();
      } catch {
        // Garder le message d'erreur par défaut
      }
    }

    throw new ApiClientError(errorMessage, response.status, errorDetails);
  }

  // Gérer les réponses vides
  const contentType = response.headers.get("content-type");
  if (!contentType || !contentType.includes("application/json")) {
    return {} as T;
  }

  return response.json();
}

export async function apiRequest<T>(
  endpoint: string,
  options?: RequestInit,
  retryOn401: boolean = true
): Promise<T> {
  const baseUrl = getApiBaseUrl();
  const url = `${baseUrl}${endpoint}`;

  // Récupérer la locale depuis le store (si disponible côté client)
  let locale = "fr";
  if (typeof window !== "undefined") {
    try {
      // Lire depuis localStorage directement pour éviter les problèmes de SSR
      const stored = localStorage.getItem("locale-preferences");
      if (stored) {
        const parsed = JSON.parse(stored);
        if (parsed.state?.locale) {
          locale = parsed.state.locale;
        }
      }
    } catch {
      // Fallback silencieux si localStorage n'est pas disponible
    }
  }

  const config: RequestInit = {
    ...options,
    headers: {
      "Content-Type": "application/json",
      "Accept-Language": locale, // Envoyer la locale au backend
      ...options?.headers,
    },
    credentials: "include", // Important pour les cookies HTTP-only
  };

  try {
    const response = await fetch(url, config);

    // Si 401 et qu'on peut retry, tenter un refresh automatique
    if (
      response.status === 401 &&
      retryOn401 &&
      endpoint !== "/api/auth/refresh" &&
      endpoint !== "/api/auth/login"
    ) {
      // Attendre que le refresh soit terminé
      const refreshSuccess = await refreshAccessToken();

      if (refreshSuccess) {
        // Réessayer la requête originale avec le nouveau token
        return apiRequest<T>(endpoint, options, false); // Ne pas retry à nouveau pour éviter les boucles
      } else {
        // Refresh échoué, l'utilisateur doit se reconnecter
        // Ne pas déclencher de déconnexion automatique ici, laisser le composant gérer
        throw new ApiClientError("Session expirée. Veuillez vous reconnecter.", 401);
      }
    }

    return handleResponse<T>(response);
  } catch (error) {
    if (error instanceof ApiClientError) {
      throw error;
    }

    // Améliorer le message d'erreur pour les erreurs réseau
    let errorMessage = "Erreur réseau";
    if (error instanceof TypeError && error.message.includes("fetch")) {
      errorMessage = `Impossible de se connecter au serveur. Vérifiez que le backend est démarré sur ${baseUrl}`;
    } else if (error instanceof Error) {
      errorMessage = error.message;
    }

    throw new ApiClientError(errorMessage, 0, { originalError: error, url });
  }
}

// Méthodes helper
export const api = {
  get: <T>(endpoint: string, options?: RequestInit) =>
    apiRequest<T>(endpoint, { ...options, method: "GET" }),

  post: <T>(endpoint: string, data?: unknown, options?: RequestInit) => {
    const requestInit: RequestInit = {
      ...options,
      method: "POST",
    };
    if (data !== undefined) {
      requestInit.body = JSON.stringify(data);
    }
    return apiRequest<T>(endpoint, requestInit);
  },

  put: <T>(endpoint: string, data?: unknown, options?: RequestInit) => {
    const requestInit: RequestInit = {
      ...options,
      method: "PUT",
    };
    if (data !== undefined) {
      requestInit.body = JSON.stringify(data);
    }
    return apiRequest<T>(endpoint, requestInit);
  },

  patch: <T>(endpoint: string, data?: unknown, options?: RequestInit) => {
    const requestInit: RequestInit = {
      ...options,
      method: "PATCH",
    };
    if (data !== undefined) {
      requestInit.body = JSON.stringify(data);
    }
    return apiRequest<T>(endpoint, requestInit);
  },

  delete: <T>(endpoint: string, options?: RequestInit) =>
    apiRequest<T>(endpoint, { ...options, method: "DELETE" }),
};
