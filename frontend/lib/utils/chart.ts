/**
 * Utilitaires et constantes partagés pour les graphiques Recharts.
 * Centralise le style du Tooltip pour garantir la cohérence visuelle entre tous les charts.
 */

/** Style du tooltip Recharts — adapté au thème via CSS variables. */
export const RECHARTS_TOOLTIP_STYLE = {
  backgroundColor: "var(--color-popover)",
  border: "1px solid var(--color-border)",
  borderRadius: "8px",
  color: "var(--color-popover-foreground)",
} as const;
