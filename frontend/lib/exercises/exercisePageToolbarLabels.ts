import type { ContentListFilterToolbarLabels } from "@/components/shared/ContentListProgressiveFilterToolbar";

/** Narrow translator for `useTranslations("exercises")` passed into toolbar label builder. */
export type ExercisesPageNamespaceT = (
  key: string,
  values?: Record<string, string | number | Date>
) => string;

export function buildExercisePageToolbarLabels(
  t: ExercisesPageNamespaceT
): ContentListFilterToolbarLabels {
  return {
    filterButton: t("filters.moreFilters"),
    filterButtonAriaExpand: t("filters.expandFilters"),
    filterButtonAriaCollapse: t("filters.collapseFilters"),
    advancedRegionLabel: t("filters.advancedFiltersRegion"),
    reset: t("filters.reset"),
    typeHeading: t("filters.exerciseType"),
    allTypes: t("filters.allTypes"),
    ageGroup: t("filters.ageGroup"),
    allAgesPlaceholder: t("filters.allAgeGroups"),
    orderLabel: t("filters.order"),
    orderAria: t("filters.order"),
    orderRandom: t("filters.orderRandom"),
    orderRecent: t("filters.orderRecent"),
    hideCompleted: t("filters.hideCompleted"),
    searchPlaceholder: t("search.placeholder"),
    searchAriaLabel: t("search.placeholder"),
    activeFiltersSummary: t("filters.activeFiltersSummary"),
    removeTypeChip: t("filters.removeTypeFilter"),
    removeAgeChip: t("filters.removeAgeFilter"),
  };
}
