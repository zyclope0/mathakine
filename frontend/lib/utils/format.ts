/**
 * Utilitaires de formatage pour l'affichage
 */

/**
 * Vérifie si un champ `tags` contient le tag "ai".
 * Gère les deux formats possibles : tableau ou chaîne séparée par virgules.
 */
export function hasAiTag(tags: string | string[] | null | undefined): boolean {
  if (!tags) return false;
  if (Array.isArray(tags)) return tags.includes("ai");
  return (
    tags === "ai" ||
    tags
      .split(",")
      .map((t) => t.trim())
      .includes("ai")
  );
}

/**
 * Formate un taux de réussite pour l'affichage.
 * Gère les deux formats possibles : ratio (0-1) ou pourcentage (0-100).
 *
 * @param rate - Le taux de réussite (peut être un ratio 0-1 ou un pourcentage 0-100)
 * @returns Le pourcentage formaté ou null si invalide
 */
export function formatSuccessRate(rate: number | null | undefined): string | null {
  if (rate === null || rate === undefined || rate < 0) {
    return null;
  }
  // Si > 1, c'est déjà un pourcentage (ex: 75 pour 75%)
  // Sinon, c'est un ratio (ex: 0.75 pour 75%)
  const percentage = rate > 1 ? Math.round(rate) : Math.round(rate * 100);
  return `${percentage}%`;
}
