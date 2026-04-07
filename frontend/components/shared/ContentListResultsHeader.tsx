"use client";

import type { ReactNode } from "react";
import { ContentListViewModeToggle } from "@/components/shared/ContentListViewModeToggle";
import { Skeleton } from "@/components/ui/skeleton";
import type { ContentListViewMode } from "@/lib/contentList/viewMode";

export interface ContentListResultsHeaderProps {
  isLoading: boolean;
  loadingLabel: string;
  /** Title row when the list is not in its initial loading state (any ReactNode from the parent). */
  titleContent: ReactNode;
  viewMode: ContentListViewMode;
  onViewModeChange: (mode: ContentListViewMode) => void;
  ariaLabelGrid: string;
  ariaLabelList: string;
}

/**
 * Shared list results header: count/title row + grid/list toggle.
 * Domain pages supply translated strings and title content.
 */
export function ContentListResultsHeader({
  isLoading,
  loadingLabel,
  titleContent,
  viewMode,
  onViewModeChange,
  ariaLabelGrid,
  ariaLabelList,
}: ContentListResultsHeaderProps) {
  return (
    <div className="flex items-center justify-between mb-2 gap-3">
      {isLoading ? (
        <div className="text-lg md:text-xl font-semibold min-h-11 flex items-center">
          <h2 className="sr-only">{loadingLabel}</h2>
          <Skeleton className="h-7 w-44 md:w-56 max-w-[min(100%,16rem)]" aria-hidden />
        </div>
      ) : (
        <h2 className="text-lg md:text-xl font-semibold">{titleContent}</h2>
      )}

      <ContentListViewModeToggle
        viewMode={viewMode}
        onViewModeChange={onViewModeChange}
        ariaLabelGrid={ariaLabelGrid}
        ariaLabelList={ariaLabelList}
      />
    </div>
  );
}
