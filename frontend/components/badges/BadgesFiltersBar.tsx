"use client";

/**
 * BadgesFiltersBar — barre de filtres et de tri.
 * Composant purement visuel.
 * FFI-L12.
 */

import { Filter, X, Target } from "lucide-react";
import { PageSection } from "@/components/layout";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { cn } from "@/lib/utils";
import type { FilterStatus, SortBy } from "@/lib/badges/badgesPage";

interface BadgesFiltersBarProps {
  filterStatus: FilterStatus;
  onFilterStatusChange: (v: FilterStatus) => void;
  filterCategory: string;
  onFilterCategoryChange: (v: string) => void;
  filterDifficulty: string;
  onFilterDifficultyChange: (v: string) => void;
  sortBy: SortBy;
  onSortByChange: (v: SortBy) => void;
  hasActiveFilters: boolean;
  onClearFilters: () => void;
  isToUnlockTab: boolean;
  closeCount: number;
  categories: string[];
  difficulties: string[];

  // Labels i18n
  filtersTitle: string;
  statusLabel: string;
  statusAll: string;
  statusEarned: string;
  statusLocked: string;
  statusClose: string;
  formatStatusClose: (count: number) => string;
  filtersReset: string;
  categoryLabel: string;
  categoryAll: string;
  formatCategory: (c: string) => string;
  difficultyLabel: string;
  difficultyAll: string;
  formatDifficulty: (d: string) => string;
  sortLabel: string;
  sortProgress: string;
  sortDate: string;
  sortPoints: string;
  sortCategory: string;
}

export function BadgesFiltersBar({
  filterStatus,
  onFilterStatusChange,
  filterCategory,
  onFilterCategoryChange,
  filterDifficulty,
  onFilterDifficultyChange,
  sortBy,
  onSortByChange,
  hasActiveFilters,
  onClearFilters,
  isToUnlockTab,
  closeCount,
  categories,
  difficulties,
  filtersTitle,
  statusLabel,
  statusAll,
  statusEarned,
  statusLocked,
  statusClose,
  formatStatusClose,
  filtersReset,
  categoryLabel,
  categoryAll,
  formatCategory,
  difficultyLabel,
  difficultyAll,
  formatDifficulty,
  sortLabel,
  sortProgress,
  sortDate,
  sortPoints,
  sortCategory,
}: BadgesFiltersBarProps) {
  return (
    <PageSection className="space-y-4 animate-fade-in-up">
      <div className="flex flex-col sm:flex-row sm:items-center gap-4">
        <div className="flex items-center gap-3 flex-wrap">
          <div className="flex items-center gap-2">
            <Filter className="h-5 w-5 text-primary" aria-hidden="true" />
            <h2 className="text-lg font-semibold">{filtersTitle}</h2>
          </div>
          {isToUnlockTab && closeCount > 0 && (
            <Button
              variant={filterStatus === "close" ? "default" : "outline"}
              size="sm"
              onClick={() => onFilterStatusChange("close")}
              className={cn(
                "shrink-0",
                filterStatus === "close" &&
                  "ring-2 ring-primary ring-offset-2 ring-offset-background"
              )}
            >
              <Target className="h-4 w-4 mr-1" aria-hidden="true" />
              {formatStatusClose(closeCount)}
            </Button>
          )}
          {hasActiveFilters && (
            <Button variant="ghost" size="sm" onClick={onClearFilters} className="gap-1 shrink-0">
              <X className="h-4 w-4" aria-hidden="true" />
              {filtersReset}
            </Button>
          )}
        </div>
      </div>
      <div className="flex flex-wrap items-center gap-4 pt-1 border-t border-border/40">
        <div className="flex items-center gap-2">
          <label htmlFor="filter-status" className="text-sm text-muted-foreground">
            {statusLabel}
          </label>
          <Select
            value={!isToUnlockTab && filterStatus === "close" ? "locked" : filterStatus}
            onValueChange={(v) => onFilterStatusChange(v as FilterStatus)}
          >
            <SelectTrigger id="filter-status" className="h-10 w-[160px]">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">{statusAll}</SelectItem>
              <SelectItem value="earned">{statusEarned}</SelectItem>
              <SelectItem value="locked">{statusLocked}</SelectItem>
              {isToUnlockTab && <SelectItem value="close">{statusClose}</SelectItem>}
            </SelectContent>
          </Select>
        </div>
        <div className="flex items-center gap-2">
          <label htmlFor="filter-category" className="text-sm text-muted-foreground">
            {categoryLabel}
          </label>
          <Select value={filterCategory} onValueChange={onFilterCategoryChange}>
            <SelectTrigger id="filter-category" className="h-10 w-[140px]">
              <SelectValue placeholder={categoryAll} />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">{categoryAll}</SelectItem>
              {categories.map((c) => (
                <SelectItem key={c} value={c}>
                  {formatCategory(c)}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        <div className="flex items-center gap-2">
          <label htmlFor="filter-difficulty" className="text-sm text-muted-foreground">
            {difficultyLabel}
          </label>
          <Select value={filterDifficulty} onValueChange={onFilterDifficultyChange}>
            <SelectTrigger id="filter-difficulty" className="h-10 w-[140px]">
              <SelectValue placeholder={difficultyAll} />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">{difficultyAll}</SelectItem>
              {difficulties.map((d) => (
                <SelectItem key={d} value={d}>
                  {formatDifficulty(d)}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        <div className="flex items-center gap-2">
          <label htmlFor="sort-by" className="text-sm text-muted-foreground">
            {sortLabel}
          </label>
          <Select value={sortBy} onValueChange={(v) => onSortByChange(v as SortBy)}>
            <SelectTrigger id="sort-by" className="h-10 w-[200px]">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="progress">{sortProgress}</SelectItem>
              <SelectItem value="date">{sortDate}</SelectItem>
              <SelectItem value="points">{sortPoints}</SelectItem>
              <SelectItem value="category">{sortCategory}</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>
    </PageSection>
  );
}
