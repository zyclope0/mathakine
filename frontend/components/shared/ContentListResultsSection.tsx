"use client";

import type { LucideIcon } from "lucide-react";
import { PageSection, PageGrid, EmptyState } from "@/components/layout";
import { Pagination } from "@/components/ui/pagination";
import { ContentListSkeleton } from "@/components/shared/ContentListSkeleton";
import { ContentListResultsHeader } from "@/components/shared/ContentListResultsHeader";
import type { ContentListViewMode } from "@/lib/contentList/viewMode";
import type { ReactNode } from "react";

export interface ContentListResultsSectionProps {
  /** Passed to PageSection (default matches exercises/challenges list block). */
  sectionClassName?: string;
  isLoading: boolean;
  error: unknown;
  errorTitle: string;
  errorDescription: string;
  errorIcon?: LucideIcon;
  loadingLabel: string;
  listHeaderTitle: ReactNode;
  itemCount: number;
  emptyTitle: string;
  emptyDescription?: string;
  emptyIcon?: LucideIcon;
  viewMode: ContentListViewMode;
  onViewModeChange: (mode: ContentListViewMode) => void;
  ariaLabelGrid: string;
  ariaLabelList: string;
  renderGrid: () => ReactNode;
  renderList: () => ReactNode;
  totalPages: number;
  currentPage: number;
  onPageChange: (page: number) => void;
  itemsPerPage: number;
  totalItems: number;
  /** Forwarded to Pagination `showInfo` when set; omit to use Pagination default. */
  paginationShowInfo?: boolean;
}

const DEFAULT_SECTION_CLASS = "space-y-3 animate-fade-in-up-delay-2";

/**
 * Orchestrates error / loading / empty / grid|list / pagination for learner content lists.
 * No domain knowledge — parents provide copy, icons, and render props.
 */
export function ContentListResultsSection({
  sectionClassName = DEFAULT_SECTION_CLASS,
  isLoading,
  error,
  errorTitle,
  errorDescription,
  errorIcon,
  loadingLabel,
  listHeaderTitle,
  itemCount,
  emptyTitle,
  emptyDescription,
  emptyIcon,
  viewMode,
  onViewModeChange,
  ariaLabelGrid,
  ariaLabelList,
  renderGrid,
  renderList,
  totalPages,
  currentPage,
  onPageChange,
  itemsPerPage,
  totalItems,
  paginationShowInfo,
}: ContentListResultsSectionProps) {
  return (
    <PageSection className={sectionClassName}>
      <ContentListResultsHeader
        isLoading={isLoading}
        loadingLabel={loadingLabel}
        titleContent={listHeaderTitle}
        viewMode={viewMode}
        onViewModeChange={onViewModeChange}
        ariaLabelGrid={ariaLabelGrid}
        ariaLabelList={ariaLabelList}
      />

      {error ? (
        <EmptyState
          title={errorTitle}
          description={errorDescription}
          {...(errorIcon !== undefined ? { icon: errorIcon } : {})}
        />
      ) : isLoading ? (
        <ContentListSkeleton variant={viewMode} loadingLabel={loadingLabel} />
      ) : itemCount === 0 ? (
        <EmptyState
          title={emptyTitle}
          {...(emptyDescription ? { description: emptyDescription } : {})}
          {...(emptyIcon !== undefined ? { icon: emptyIcon } : {})}
        />
      ) : (
        <>
          {viewMode === "grid" ? (
            <PageGrid columns={{ mobile: 1, tablet: 2, desktop: 3 }} gap="sm" className="md:gap-4">
              {renderGrid()}
            </PageGrid>
          ) : (
            renderList()
          )}

          {totalPages > 1 ? (
            <div className="mt-4 pt-4 border-t border-border/50">
              <Pagination
                currentPage={currentPage}
                totalPages={totalPages}
                onPageChange={onPageChange}
                itemsPerPage={itemsPerPage}
                totalItems={totalItems}
                {...(paginationShowInfo !== undefined ? { showInfo: paginationShowInfo } : {})}
              />
            </div>
          ) : null}
        </>
      )}
    </PageSection>
  );
}
