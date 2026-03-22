/**
 * Valeurs d'ordre pour les listes paginées (exercices, défis, etc.).
 * Aligné sur le paramètre API `order` (backend + usePaginatedContent).
 */
export const CONTENT_LIST_ORDER = {
  RANDOM: "random",
  RECENT: "recent",
} as const;

export type ContentListOrder = (typeof CONTENT_LIST_ORDER)[keyof typeof CONTENT_LIST_ORDER];
