import { CONTENT_LIST_ORDER, type ContentListOrder } from "@/lib/constants/contentListOrder";

export function contentListTotalPages(total: number, itemsPerPage: number): number {
  return Math.ceil(total / itemsPerPage) || 1;
}

export function hasActiveContentListFilters(params: {
  typeFilter: string;
  ageFilter: string;
  searchQuery: string;
  orderFilter: ContentListOrder;
  hideCompleted: boolean;
}): boolean {
  return (
    params.typeFilter !== "all" ||
    params.ageFilter !== "all" ||
    params.searchQuery.trim() !== "" ||
    params.orderFilter !== CONTENT_LIST_ORDER.RANDOM ||
    params.hideCompleted
  );
}

/**
 * Compte tous les filtres masqués dans le panneau avancé.
 * Inclut type, âge, tri (non-aléatoire) et masquer réussis.
 * Utilisé pour le badge du bouton "Plus de filtres".
 */
export function contentListAdvancedFilterActiveCount(
  typeFilter: string,
  ageFilter: string,
  orderFilter?: ContentListOrder,
  hideCompleted?: boolean
): number {
  return (
    (typeFilter !== "all" ? 1 : 0) +
    (ageFilter !== "all" ? 1 : 0) +
    (orderFilter !== undefined && orderFilter !== CONTENT_LIST_ORDER.RANDOM ? 1 : 0) +
    (hideCompleted ? 1 : 0)
  );
}
