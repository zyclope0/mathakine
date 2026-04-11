import type { ExerciseFilters } from "@/hooks/useExercises";
import type { ContentListOrder } from "@/lib/constants/contentListOrder";

export interface BuildExercisePageFiltersInput {
  itemsPerPage: number;
  currentPage: number;
  exerciseTypeFilter: string;
  ageGroupFilter: string;
  searchQuery: string;
  orderFilter: ContentListOrder;
  hideCompleted: boolean;
}

/** Builds `ExerciseFilters` for `useExercises` from shared list UI state (pagination + filters). */
export function buildExercisePageFilters(input: BuildExercisePageFiltersInput): ExerciseFilters {
  const {
    itemsPerPage,
    currentPage,
    exerciseTypeFilter,
    ageGroupFilter,
    searchQuery,
    orderFilter,
    hideCompleted,
  } = input;

  const f: ExerciseFilters = {
    limit: itemsPerPage,
    skip: (currentPage - 1) * itemsPerPage,
    order: orderFilter,
    hide_completed: hideCompleted,
  };

  if (exerciseTypeFilter !== "all") {
    f.exercise_type = exerciseTypeFilter;
  }

  if (ageGroupFilter !== "all") {
    f.age_group = ageGroupFilter;
  }

  const trimmed = searchQuery.trim();
  if (trimmed) {
    f.search = trimmed;
  }

  return f;
}
