/**
 * Utilitaires de formatage pour l'affichage
 */

/**
 * Formate une date ISO en format court localisé : "2026-02-15" → "15 fév".
 * Utilisé dans les axes X des graphiques Recharts (ProgressChart, DailyExercisesChart).
 * Retourne la valeur brute si la date est invalide.
 */
export function formatShortDate(value: string): string {
  try {
    const d = new Date(value);
    if (isNaN(d.getTime())) return value;
    return d.toLocaleDateString("fr-FR", { day: "numeric", month: "short" }).replace(".", "");
  } catch {
    return value;
  }
}

/**
 * Détermine si un exercice ou un défi a été généré par l'IA.
 * Source unique de vérité : préférer `ai_generated` (bool), sinon se rabattre sur les tags.
 */
export function isAiGenerated(item: {
  ai_generated?: boolean | null;
  tags?: string | string[] | null;
}): boolean {
  if (item.ai_generated != null) return Boolean(item.ai_generated);
  return hasAiTag(item.tags);
}

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
