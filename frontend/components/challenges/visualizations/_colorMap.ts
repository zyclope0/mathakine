/**
 * Source de vérité FR/EN → hex pour les couleurs des défis visuels / probabilités
 * (ACTIF-07-COLORMAP-01). Ordre des clés = ordre de scan dans le texte (premier match gagne).
 */

export const VISUALIZATION_COLOR_MAP: Readonly<Record<string, string>> = {
  rouge: "#ef4444",
  red: "#ef4444",
  bleu: "#3b82f6",
  blue: "#3b82f6",
  vert: "#22c55e",
  green: "#22c55e",
  jaune: "#eab308",
  yellow: "#eab308",
  orange: "#f97316",
  violet: "#a855f7",
  purple: "#a855f7",
  rose: "#ec4899",
  pink: "#ec4899",
  noir: "#1f2937",
  black: "#1f2937",
  blanc: "#f9fafb",
  white: "#f9fafb",
  gris: "#6b7280",
  gray: "#6b7280",
  brown: "#92400e",
  marron: "#92400e",
};

/**
 * Résout un nom de couleur exact (ex. layout JSON) vers une valeur CSS, ou null si inconnu.
 */
export function resolveVisualizationColor(name: string | null | undefined): string | null {
  if (!name || typeof name !== "string" || name === "?") return null;
  const key = name.toLowerCase().trim();
  return VISUALIZATION_COLOR_MAP[key] ?? null;
}

/**
 * Première couleur dont le nom apparaît en sous-chaîne dans le texte (déjà normalisé en minuscules).
 * Ordre = ordre d’insertion de {@link VISUALIZATION_COLOR_MAP}.
 */
export function findVisualizationColorInText(lowerText: string): string | null {
  for (const [colorName, colorValue] of Object.entries(VISUALIZATION_COLOR_MAP)) {
    if (lowerText.includes(colorName)) {
      return colorValue;
    }
  }
  return null;
}
