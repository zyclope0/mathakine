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
  (process.env.NODE_ENV === 'development' ? 'http://localhost:10000' : '');

// Validation en production
if (process.env.NODE_ENV === 'production' && (!API_BASE_URL || API_BASE_URL.includes('localhost'))) {
  throw new Error(
    'NEXT_PUBLIC_API_BASE_URL doit être défini en production et ne peut pas être localhost'
  );
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
    this.name = 'ApiClientError';
    this.status = status;
    this.details = details;
  }
}

// État global pour gérer le refresh en cours
let isRefreshing = false;
let refreshPromise: Promise<boolean> | null = null;

/**
 * Récupère le refresh_token depuis localStorage
 */
function getRefreshToken(): string | null {
  if (typeof window === 'undefined') return null;
  try {
    return localStorage.getItem('refresh_token');
  } catch {
    return null;
  }
}

/**
 * Stocke le refresh_token dans localStorage
 */
function setRefreshToken(token: string | null): void {
  if (typeof window === 'undefined') return;
  try {
    if (token) {
      localStorage.setItem('refresh_token', token);
    } else {
      localStorage.removeItem('refresh_token');
    }
  } catch {
    // Ignorer les erreurs de localStorage (mode privé, etc.)
  }
}

/**
 * Tente de rafraîchir le token d'accès en utilisant le refresh token
 * Le refresh token est envoyé dans le body de la requête pour supporter le cross-domain
 */
async function refreshAccessToken(): Promise<boolean> {
  // Si un refresh est déjà en cours, attendre sa fin
  if (isRefreshing && refreshPromise) {
    return refreshPromise;
  }

  isRefreshing = true;
  refreshPromise = (async () => {
    try {
      // Récupérer le refresh_token depuis localStorage
      const refreshToken = getRefreshToken();
      
      if (!refreshToken) {
        console.warn('[API Client] Aucun refresh_token trouvé pour rafraîchir le token');
        return false;
      }

      // Envoyer le refresh_token dans le body de la requête
      const response = await fetch(`${API_BASE_URL}/api/auth/refresh`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include', // Important pour les cookies HTTP-only (fallback)
        body: JSON.stringify({ refresh_token: refreshToken }),
      });

      if (response.ok) {
        // Le backend peut renvoyer un nouveau refresh_token dans la réponse
        try {
          const data = await response.json();
          if (data.refresh_token) {
            setRefreshToken(data.refresh_token);
          }
        } catch {
          // Si la réponse n'est pas du JSON, ce n'est pas grave
        }
        return true;
      } else {
        // Refresh token invalide ou expiré, nettoyer le localStorage
        setRefreshToken(null);
        return false;
      }
    } catch (error) {
      console.error('[API Client] Erreur lors du refresh du token:', error);
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
      errorMessage = errorData.message || errorData.detail || errorMessage;
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
  const contentType = response.headers.get('content-type');
  if (!contentType || !contentType.includes('application/json')) {
    return {} as T;
  }

  return response.json();
}

export async function apiRequest<T>(
  endpoint: string,
  options?: RequestInit,
  retryOn401: boolean = true
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;

  // Récupérer la locale depuis le store (si disponible côté client)
  let locale = 'fr';
  if (typeof window !== 'undefined') {
    try {
      // Lire depuis localStorage directement pour éviter les problèmes de SSR
      const stored = localStorage.getItem('locale-preferences');
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
      'Content-Type': 'application/json',
      'Accept-Language': locale, // Envoyer la locale au backend
      ...options?.headers,
    },
    credentials: 'include', // Important pour les cookies HTTP-only
  };

  try {
    const response = await fetch(url, config);
    
    // Si 401 et qu'on peut retry, tenter un refresh automatique
    if (response.status === 401 && retryOn401 && endpoint !== '/api/auth/refresh' && endpoint !== '/api/auth/login') {
      // Attendre que le refresh soit terminé
      const refreshSuccess = await refreshAccessToken();
      
      if (refreshSuccess) {
        // Réessayer la requête originale avec le nouveau token
        return apiRequest<T>(endpoint, options, false); // Ne pas retry à nouveau pour éviter les boucles
      } else {
        // Refresh échoué, l'utilisateur doit se reconnecter
        // Ne pas déclencher de déconnexion automatique ici, laisser le composant gérer
        throw new ApiClientError('Session expirée. Veuillez vous reconnecter.', 401);
      }
    }
    
    return handleResponse<T>(response);
  } catch (error) {
    if (error instanceof ApiClientError) {
      throw error;
    }
    
    // Améliorer le message d'erreur pour les erreurs réseau
    let errorMessage = 'Erreur réseau';
    if (error instanceof TypeError && error.message.includes('fetch')) {
      errorMessage = `Impossible de se connecter au serveur. Vérifiez que le backend est démarré sur ${API_BASE_URL}`;
    } else if (error instanceof Error) {
      errorMessage = error.message;
    }
    
    throw new ApiClientError(
      errorMessage,
      0,
      { originalError: error, url }
    );
  }
}

// Méthodes helper
export const api = {
  get: <T>(endpoint: string, options?: RequestInit) =>
    apiRequest<T>(endpoint, { ...options, method: 'GET' }),

  post: <T>(endpoint: string, data?: unknown, options?: RequestInit) => {
    const requestInit: RequestInit = {
      ...options,
      method: 'POST',
    };
    if (data !== undefined) {
      requestInit.body = JSON.stringify(data);
    }
    return apiRequest<T>(endpoint, requestInit);
  },

  put: <T>(endpoint: string, data?: unknown, options?: RequestInit) => {
    const requestInit: RequestInit = {
      ...options,
      method: 'PUT',
    };
    if (data !== undefined) {
      requestInit.body = JSON.stringify(data);
    }
    return apiRequest<T>(endpoint, requestInit);
  },

  patch: <T>(endpoint: string, data?: unknown, options?: RequestInit) => {
    const requestInit: RequestInit = {
      ...options,
      method: 'PATCH',
    };
    if (data !== undefined) {
      requestInit.body = JSON.stringify(data);
    }
    return apiRequest<T>(endpoint, requestInit);
  },

  delete: <T>(endpoint: string, options?: RequestInit) =>
    apiRequest<T>(endpoint, { ...options, method: 'DELETE' }),
};

