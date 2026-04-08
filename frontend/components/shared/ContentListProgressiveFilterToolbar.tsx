"use client";

import { useId } from "react";
import { cn } from "@/lib/utils";
import { CONTENT_LIST_ORDER, type ContentListOrder } from "@/lib/constants/contentListOrder";
import { ContentListToolbarSearchRow } from "@/components/shared/ContentListToolbarSearchRow";
import { ContentListToolbarTypeChips } from "@/components/shared/ContentListToolbarTypeChips";
import { ContentListToolbarSummary } from "@/components/shared/ContentListToolbarSummary";
import { ContentListToolbarAdvancedPanel } from "@/components/shared/ContentListToolbarAdvancedPanel";
import type { TypeStyleMap } from "@/components/shared/contentListToolbarTypes";

export type { TypeStyleMap } from "@/components/shared/contentListToolbarTypes";

/** Libellés passés par la page (next-intl) — pas de chaînes magiques dans le composant. */
export interface ContentListFilterToolbarLabels {
  filterButton: string;
  filterButtonAriaExpand: string;
  filterButtonAriaCollapse: string;
  advancedRegionLabel: string;
  reset: string;
  typeHeading: string;
  allTypes: string;
  ageGroup: string;
  allAgesPlaceholder: string;
  orderLabel: string;
  orderAria: string;
  orderRandom: string;
  orderRecent: string;
  hideCompleted: string;
  searchPlaceholder: string;
  searchAriaLabel: string;
  activeFiltersSummary: string;
  removeTypeChip: string;
  removeAgeChip: string;
}

export interface ContentListProgressiveFilterToolbarProps {
  labels: ContentListFilterToolbarLabels;
  searchQuery: string;
  onSearchChange: (value: string) => void;
  onSearchPageReset: () => void;
  panelOpen: boolean;
  onPanelOpenChange: (open: boolean) => void;
  typeFilterValue: string;
  onTypeFilterChange: (value: string) => void;
  typeStyles: TypeStyleMap;
  ageFilterValue: string;
  onAgeFilterChange: (value: string) => void;
  ageGroupValues: readonly string[];
  orderValue: ContentListOrder;
  onOrderChange: (value: ContentListOrder) => void;
  hideCompleted: boolean;
  onHideCompletedChange: (checked: boolean) => void;
  hideCompletedFieldId: string;
  getTypeDisplay: (typeKey: string) => string;
  getAgeDisplay: (ageKey: string) => string;
  onResetAll: () => void;
  onFilterAdjust: () => void;
  onClearTypeFilter: () => void;
  onClearAgeFilter: () => void;
  /** Afficher le bouton reset dans le panneau (tout état filtré). */
  hasResettableState: boolean;
  /** Nombre de filtres avancés actifs (type, âge, ordre, hideCompleted) pour le badge. */
  advancedActiveCount: number;
  containerClassName?: string;
  /**
   * Si true : les chips de filtre par type sont affichées directement sous la barre de
   * recherche (accès en 1 clic, icône + label visible). Le panneau avancé ne garde que
   * âge, ordre et masquer les réussis.
   * Défaut false — rétrocompatible avec les pages qui n'utilisent pas ce mode.
   */
  showTypeChipsInline?: boolean;
}

export function ContentListProgressiveFilterToolbar({
  labels,
  searchQuery,
  onSearchChange,
  onSearchPageReset,
  panelOpen,
  onPanelOpenChange,
  typeFilterValue,
  onTypeFilterChange,
  typeStyles,
  ageFilterValue,
  onAgeFilterChange,
  ageGroupValues,
  orderValue,
  onOrderChange,
  hideCompleted,
  onHideCompletedChange,
  hideCompletedFieldId,
  getTypeDisplay,
  getAgeDisplay,
  onResetAll,
  onFilterAdjust,
  onClearTypeFilter,
  onClearAgeFilter,
  hasResettableState,
  advancedActiveCount,
  containerClassName,
  showTypeChipsInline = false,
}: ContentListProgressiveFilterToolbarProps) {
  const baseId = useId();
  const panelId = `${baseId}-advanced-panel`;
  const regionTitleId = `${baseId}-advanced-title`;

  const showTypeChip = typeFilterValue !== "all" && !showTypeChipsInline;
  const showAgeChip = ageFilterValue !== "all";
  const hasSummaryChips = showTypeChip || showAgeChip;

  const orderActive = orderValue !== CONTENT_LIST_ORDER.RANDOM;
  const stateSummaryParts: string[] = [];
  if (orderActive)
    stateSummaryParts.push(
      orderValue === CONTENT_LIST_ORDER.RECENT ? labels.orderRecent : labels.orderRandom
    );
  if (hideCompleted) stateSummaryParts.push(labels.hideCompleted);
  const showStateSummary = !panelOpen && stateSummaryParts.length > 0;

  const filterToggleAriaLabel = panelOpen
    ? [labels.filterButton, labels.filterButtonAriaCollapse].filter(Boolean).join(" — ")
    : [labels.filterButton, labels.filterButtonAriaExpand].filter(Boolean).join(" — ");

  return (
    <div
      className={cn(
        "p-4 rounded-xl border border-border/50 bg-card flex flex-col gap-3 animate-fade-in-up min-w-0",
        containerClassName
      )}
    >
      <ContentListToolbarSearchRow
        searchPlaceholder={labels.searchPlaceholder}
        searchAriaLabel={labels.searchAriaLabel}
        searchQuery={searchQuery}
        onSearchChange={onSearchChange}
        onSearchPageReset={onSearchPageReset}
        filterButtonLabel={labels.filterButton}
        filterToggleAriaLabel={filterToggleAriaLabel}
        filterToggleId={`${baseId}-filter-toggle`}
        panelOpen={panelOpen}
        onPanelOpenChange={onPanelOpenChange}
        panelId={panelId}
        advancedActiveCount={advancedActiveCount}
      />

      {showTypeChipsInline ? (
        <ContentListToolbarTypeChips
          typeHeadingAriaLabel={labels.typeHeading}
          allTypesLabel={labels.allTypes}
          typeFilterValue={typeFilterValue}
          onTypeFilterChange={onTypeFilterChange}
          onFilterAdjust={onFilterAdjust}
          typeStyles={typeStyles}
          getTypeDisplay={getTypeDisplay}
        />
      ) : null}

      <ContentListToolbarSummary
        showStateSummary={showStateSummary}
        stateSummaryText={stateSummaryParts.join(" · ")}
        hasSummaryChips={hasSummaryChips}
        activeFiltersSummaryAriaLabel={labels.activeFiltersSummary}
        showTypeChip={showTypeChip}
        typeChipLabel={getTypeDisplay(typeFilterValue)}
        onClearTypeFilter={onClearTypeFilter}
        removeTypeChipAriaLabel={labels.removeTypeChip}
        showAgeChip={showAgeChip}
        ageChipLabel={getAgeDisplay(ageFilterValue)}
        onClearAgeFilter={onClearAgeFilter}
        removeAgeChipAriaLabel={labels.removeAgeChip}
      />

      <ContentListToolbarAdvancedPanel
        panelId={panelId}
        regionTitleId={regionTitleId}
        panelOpen={panelOpen}
        advancedRegionLabel={labels.advancedRegionLabel}
        showTypeChipsInline={showTypeChipsInline}
        typeHeading={labels.typeHeading}
        allTypesLabel={labels.allTypes}
        typeFilterValue={typeFilterValue}
        onTypeFilterChange={onTypeFilterChange}
        onFilterAdjust={onFilterAdjust}
        typeStyles={typeStyles}
        getTypeDisplay={getTypeDisplay}
        ageFieldId={`${baseId}-age`}
        ageGroupLabel={labels.ageGroup}
        allAgesPlaceholder={labels.allAgesPlaceholder}
        ageFilterValue={ageFilterValue}
        onAgeFilterChange={onAgeFilterChange}
        ageGroupValues={ageGroupValues}
        getAgeDisplay={getAgeDisplay}
        orderFieldId={`${baseId}-order`}
        orderLabel={labels.orderLabel}
        orderAria={labels.orderAria}
        orderRandom={labels.orderRandom}
        orderRecent={labels.orderRecent}
        orderValue={orderValue}
        onOrderChange={onOrderChange}
        hideCompletedFieldId={hideCompletedFieldId}
        hideCompleted={hideCompleted}
        onHideCompletedChange={onHideCompletedChange}
        hideCompletedLabel={labels.hideCompleted}
        hasResettableState={hasResettableState}
        resetLabel={labels.reset}
        onResetAll={onResetAll}
      />
    </div>
  );
}
