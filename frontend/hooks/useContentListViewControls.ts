"use client";

import { useCallback, useState } from "react";
import type { ContentListViewMode } from "@/lib/contentList/viewMode";

/**
 * Shared pagination + grid/list view toggling for content list pages (exercises, challenges).
 */
export function useContentListViewControls() {
  const [currentPage, setCurrentPage] = useState(1);
  const [viewMode, setViewMode] = useState<ContentListViewMode>("grid");

  const handleFilterChange = useCallback(() => {
    setCurrentPage(1);
  }, []);

  const handlePageChange = useCallback((page: number) => {
    setCurrentPage(page);
    window.scrollTo({ top: 0, behavior: "smooth" });
  }, []);

  return {
    currentPage,
    setCurrentPage,
    viewMode,
    setViewMode,
    handleFilterChange,
    handlePageChange,
  };
}
