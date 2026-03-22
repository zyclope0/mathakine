/**
 * Classification des widgets de l’onglet Progression (dashboard).
 * Sert de référence unique pour la doc produit / revues — pas de logique runtime critique.
 */
export const PROGRESS_TAB_WIDGET_SCOPE = {
  /** useProgressTimeline — 7j / 30j */
  timeline: "local-period",
  /** useProgressTimeline(period) — même période que la timeline ; widget « Régularité » */
  practiceConsistency: "local-period",
  /** GET /api/users/me/progress — agrégat global */
  categoryAccuracy: "cumulative",
  /** idem */
  volumeByType: "cumulative",
  /** progression défis agrégée */
  challengesProgress: "cumulative",
} as const;

export type ProgressTabWidgetScope =
  (typeof PROGRESS_TAB_WIDGET_SCOPE)[keyof typeof PROGRESS_TAB_WIDGET_SCOPE];

/**
 * V3 (hors scope) : endpoints `progress` / `challenges` pourraient accepter un `timeRange`
 * optionnel pour aligner précision & volume sur une période sans changer l’API publique existante
 * en mode défaut « all-time ».
 */
