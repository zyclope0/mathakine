"use client";

import type { ReactNode } from "react";
import { ExerciseCard } from "@/components/exercises/ExerciseCard";
import { CompactListItem } from "@/components/shared/CompactListItem";
import { ContentListResultsSection } from "@/components/shared/ContentListResultsSection";
import { getStaggerDelay } from "@/lib/utils/animation";
import { isAiGenerated } from "@/lib/utils/format";
import { EXERCISE_TYPE_STYLES } from "@/lib/constants/exercises";
import type { Exercise } from "@/types/api";
import type { ContentListViewMode } from "@/lib/contentList/viewMode";
import { ApiClientError } from "@/lib/api/client";
import type { ExercisesPageNamespaceT } from "@/lib/exercises/exercisePageToolbarLabels";

export interface ExercisesResultsViewProps {
  t: ExercisesPageNamespaceT;
  listHeaderTitle: ReactNode;
  isLoading: boolean;
  error: unknown;
  exercises: Exercise[];
  searchQuery: string;
  viewMode: ContentListViewMode;
  onViewModeChange: (mode: ContentListViewMode) => void;
  totalPages: number;
  currentPage: number;
  onPageChange: (page: number) => void;
  itemsPerPage: number;
  totalItems: number;
  isCompleted: (id: number) => boolean;
  openItem: (id: number) => void;
  getTypeDisplay: (type: string | null | undefined) => string;
  getAgeDisplay: (age: string | null | undefined) => string;
}

export function ExercisesResultsView({
  t,
  listHeaderTitle,
  isLoading,
  error,
  exercises,
  searchQuery,
  viewMode,
  onViewModeChange,
  totalPages,
  currentPage,
  onPageChange,
  itemsPerPage,
  totalItems,
  isCompleted,
  openItem,
  getTypeDisplay,
  getAgeDisplay,
}: ExercisesResultsViewProps) {
  return (
    <ContentListResultsSection
      isLoading={isLoading}
      error={error}
      errorTitle={t("list.error.title", { default: "Erreur de chargement" })}
      errorDescription={
        error instanceof ApiClientError
          ? error.message
          : t("list.error.description", { default: "Impossible de charger les exercices" })
      }
      loadingLabel={t("list.loading")}
      listHeaderTitle={listHeaderTitle}
      itemCount={exercises.length}
      emptyTitle={
        searchQuery.trim() ? t("search.noResults", { query: searchQuery }) : t("list.empty")
      }
      emptyDescription={searchQuery.trim() ? "" : t("list.emptyHint")}
      viewMode={viewMode}
      onViewModeChange={onViewModeChange}
      ariaLabelGrid={t("viewGrid")}
      ariaLabelList={t("viewList")}
      renderGrid={() =>
        exercises.map((exercise, index) => (
          <div key={exercise.id} className={`${getStaggerDelay(index)} h-full`}>
            <ExerciseCard
              exercise={exercise}
              completed={isCompleted(exercise.id)}
              onOpen={openItem}
            />
          </div>
        ))
      }
      renderList={() => (
        <div className="space-y-2">
          {exercises.map((exercise) => {
            const typeKey =
              exercise.exercise_type?.toLowerCase() as keyof typeof EXERCISE_TYPE_STYLES;
            const { icon: TypeIcon } = EXERCISE_TYPE_STYLES[typeKey] || EXERCISE_TYPE_STYLES.divers;
            return (
              <CompactListItem
                key={exercise.id}
                title={exercise.title}
                subtitle={exercise.question}
                TypeIcon={TypeIcon}
                aiGenerated={isAiGenerated(exercise)}
                completed={isCompleted(exercise.id)}
                typeDisplay={getTypeDisplay(exercise.exercise_type)}
                ageDisplay={getAgeDisplay(exercise.age_group)}
                onClick={() => openItem(exercise.id)}
              />
            );
          })}
        </div>
      )}
      totalPages={totalPages}
      currentPage={currentPage}
      onPageChange={onPageChange}
      itemsPerPage={itemsPerPage}
      totalItems={totalItems}
      paginationShowInfo
    />
  );
}
