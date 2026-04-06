"use client";

/**
 * BadgesCollectionSection — collection badges obtenue avec collapse et pinning.
 * Composant purement visuel.
 * FFI-L12.
 */

import { ChevronDown, ChevronUp, AlertCircle, RefreshCw } from "lucide-react";
import { PageSection } from "@/components/layout";
import { LoadingState, EmptyState } from "@/components/layout";
import { BadgeGrid } from "@/components/badges/BadgeGrid";
import { Button } from "@/components/ui/button";
import type { Badge, UserBadge } from "@/types/api";
import type { RarityInfo } from "@/components/badges/BadgeGrid";
import type { SortBy } from "@/lib/badges/badgesPage";

interface BadgesCollectionSectionProps {
  filteredEarned: Badge[];
  sortedEarned: Badge[];
  earnedBadges: UserBadge[];
  sortBy: SortBy;
  rarityMap: Record<string, RarityInfo>;
  pinnedBadgeIds: number[];
  onTogglePin: (badgeId: number) => Promise<void>;
  collectionExpanded: boolean;
  onToggleExpanded: () => void;
  isLoading: boolean;
  error: Error | string | null;
  hasActiveFilters: boolean;
  totalCount: number;

  // Labels i18n
  title: string;
  formatCount: (earned: number, total: number) => string;
  errorTitle: string;
  errorDescription: string;
  errorRetry: string;
  loadingMessage: string;
  noResults: string;
  emptyLabel: string;
  collapseCollection: string;
  formatViewFull: (count: number) => string;
  showLess: string;
  showMore: string;
}

const COLLECTION_PREVIEW_COUNT = 12;

export function BadgesCollectionSection({
  filteredEarned,
  sortedEarned,
  earnedBadges,
  sortBy,
  rarityMap,
  pinnedBadgeIds,
  onTogglePin,
  collectionExpanded,
  onToggleExpanded,
  isLoading,
  error,
  hasActiveFilters,
  totalCount,
  title,
  formatCount,
  errorTitle,
  errorDescription,
  errorRetry,
  loadingMessage,
  noResults,
  emptyLabel,
  collapseCollection,
  formatViewFull,
}: BadgesCollectionSectionProps) {
  const earnedForDisplay = earnedBadges.filter((ub) => filteredEarned.some((b) => b.id === ub.id));

  return (
    <PageSection className="space-y-4 animate-fade-in-up-delay-1">
      <h2 className="text-lg md:text-xl font-semibold">
        {title} {formatCount(filteredEarned.length, filteredEarned.length + 0 || totalCount)}
      </h2>
      {error ? (
        <EmptyState
          title={errorTitle}
          description={error instanceof Error ? error.message : errorDescription}
          icon={AlertCircle}
          action={
            <Button variant="outline" onClick={() => window.location.reload()}>
              <RefreshCw className="mr-2 h-4 w-4" />
              {errorRetry}
            </Button>
          }
        />
      ) : isLoading ? (
        <LoadingState message={loadingMessage} />
      ) : filteredEarned.length > 0 ? (
        <div className="relative space-y-4">
          <div className="relative">
            <BadgeGrid
              badges={sortedEarned}
              earnedBadges={earnedForDisplay}
              isLoading={false}
              sortBy={sortBy}
              rarityMap={rarityMap}
              pinnedBadgeIds={pinnedBadgeIds}
              compactEarned
              {...(!collectionExpanded && {
                limit: COLLECTION_PREVIEW_COUNT,
              })}
              onTogglePin={async (badgeId) => {
                await onTogglePin(badgeId);
              }}
            />
            {!collectionExpanded && filteredEarned.length > COLLECTION_PREVIEW_COUNT && (
              <div
                className="absolute bottom-0 left-0 right-0 h-24 bg-gradient-to-t from-background to-transparent pointer-events-none"
                aria-hidden="true"
              />
            )}
          </div>
          {filteredEarned.length > COLLECTION_PREVIEW_COUNT && (
            <div className="flex justify-center">
              <Button
                variant="outline"
                onClick={onToggleExpanded}
                aria-expanded={collectionExpanded}
              >
                {collectionExpanded ? (
                  <>
                    <ChevronUp className="h-4 w-4 mr-2" aria-hidden="true" />
                    {collapseCollection}
                  </>
                ) : (
                  <>
                    <ChevronDown className="h-4 w-4 mr-2" aria-hidden="true" />
                    {formatViewFull(filteredEarned.length)}
                  </>
                )}
              </Button>
            </div>
          )}
        </div>
      ) : (
        <p className="text-muted-foreground py-6" role="status">
          {hasActiveFilters ? noResults : emptyLabel}
        </p>
      )}
    </PageSection>
  );
}
