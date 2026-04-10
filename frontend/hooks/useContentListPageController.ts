"use client";

import { useCallback, useMemo, useState } from "react";
import { type STORAGE_KEYS } from "@/lib/storage";
import {
  contentListAdvancedFilterActiveCount,
  hasActiveContentListFilters,
} from "@/lib/contentList/pageHelpers";
import { useContentListOrderPreference } from "@/hooks/useContentListOrderPreference";
import { useContentListViewControls } from "@/hooks/useContentListViewControls";

export type ContentListPageOrderPreferenceStorageKey =
  | typeof STORAGE_KEYS.prefExerciseOrder
  | typeof STORAGE_KEYS.prefChallengeOrder;

export interface UseContentListPageControllerOptions {
  orderPreferenceStorageKey: ContentListPageOrderPreferenceStorageKey;
}

/**
 * Composes shared list UI state for learner content-list pages (exercises, challenges).
 * Does not fetch data or run domain-specific effects.
 */
export function useContentListPageController(options: UseContentListPageControllerOptions) {
  const { orderPreferenceStorageKey } = options;

  const [typeFilter, setTypeFilter] = useState("all");
  const [ageFilter, setAgeFilter] = useState("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [filtersPanelOpen, setFiltersPanelOpen] = useState(false);
  const [hideCompleted, setHideCompleted] = useState(false);
  const [selectedItemId, setSelectedItemId] = useState<number | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const {
    currentPage,
    setCurrentPage,
    viewMode,
    setViewMode,
    handleFilterChange,
    handlePageChange,
  } = useContentListViewControls();

  const { orderFilter, handleOrderChange, resetOrderPreference } =
    useContentListOrderPreference(orderPreferenceStorageKey);

  const hasActiveFilters = useMemo(
    () =>
      hasActiveContentListFilters({
        typeFilter,
        ageFilter,
        searchQuery,
        orderFilter,
        hideCompleted,
      }),
    [typeFilter, ageFilter, searchQuery, orderFilter, hideCompleted]
  );

  const advancedActiveCount = useMemo(
    () => contentListAdvancedFilterActiveCount(typeFilter, ageFilter, orderFilter, hideCompleted),
    [typeFilter, ageFilter, orderFilter, hideCompleted]
  );

  const clearFilters = useCallback(() => {
    setTypeFilter("all");
    setAgeFilter("all");
    setSearchQuery("");
    resetOrderPreference();
    setHideCompleted(false);
    setCurrentPage(1);
  }, [resetOrderPreference, setCurrentPage]);

  const clearTypeFilter = useCallback(() => {
    setTypeFilter("all");
    handleFilterChange();
  }, [handleFilterChange]);

  const clearAgeFilter = useCallback(() => {
    setAgeFilter("all");
    handleFilterChange();
  }, [handleFilterChange]);

  const openItem = useCallback((id: number) => {
    setSelectedItemId(id);
    setIsModalOpen(true);
  }, []);

  const closeModal = useCallback(() => {
    setIsModalOpen(false);
    setSelectedItemId(null);
  }, []);

  const handleModalOpenChange = useCallback((open: boolean) => {
    setIsModalOpen(open);
    if (!open) setSelectedItemId(null);
  }, []);

  return {
    typeFilter,
    setTypeFilter,
    ageFilter,
    setAgeFilter,
    searchQuery,
    setSearchQuery,
    filtersPanelOpen,
    setFiltersPanelOpen,
    hideCompleted,
    setHideCompleted,
    selectedItemId,
    isModalOpen,
    currentPage,
    setCurrentPage,
    viewMode,
    setViewMode,
    handleFilterChange,
    handlePageChange,
    orderFilter,
    handleOrderChange,
    resetOrderPreference,
    hasActiveFilters,
    advancedActiveCount,
    clearFilters,
    clearTypeFilter,
    clearAgeFilter,
    openItem,
    closeModal,
    handleModalOpenChange,
  };
}
