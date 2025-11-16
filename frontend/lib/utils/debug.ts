/**
 * Utilitaires de débogage pour le développement
 * En production, ces fonctions sont désactivées pour des raisons de performance
 */

/**
 * Log de débogage conditionnel
 * Ne log que si NODE_ENV === 'development'
 */
export function debugLog(message: string, ...args: unknown[]): void {
  if (process.env.NODE_ENV === 'development') {
    console.log(`[DEBUG] ${message}`, ...args);
  }
}

/**
 * Log d'erreur de débogage conditionnel
 */
export function debugError(message: string, error?: unknown): void {
  if (process.env.NODE_ENV === 'development') {
    console.error(`[DEBUG ERROR] ${message}`, error);
  }
}

/**
 * Log d'avertissement de débogage conditionnel
 */
export function debugWarn(message: string, ...args: unknown[]): void {
  if (process.env.NODE_ENV === 'development') {
    console.warn(`[DEBUG WARN] ${message}`, ...args);
  }
}
