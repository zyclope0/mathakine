"use client";

import { useId } from "react";
import type { LucideIcon } from "lucide-react";
import { ChevronDown, Filter, Search, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Switch } from "@/components/ui/switch";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { cn } from "@/lib/utils";
import { CONTENT_LIST_ORDER, type ContentListOrder } from "@/lib/constants/contentListOrder";

export type TypeStyleMap = Record<string, { icon: LucideIcon }>;

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

function FilterSummaryChip({
  label,
  onRemove,
  removeAriaLabel,
}: {
  label: string;
  onRemove: () => void;
  removeAriaLabel: string;
}) {
  return (
    <Badge variant="secondary" className="gap-0.5 pl-2.5 pr-1 py-1 text-xs font-normal max-w-full">
      <span className="truncate">{label}</span>
      <button
        type="button"
        className="inline-flex h-11 w-11 shrink-0 items-center justify-center rounded-sm text-muted-foreground hover:text-foreground touch-manipulation"
        aria-label={removeAriaLabel}
        onClick={onRemove}
      >
        <X className="h-4 w-4" aria-hidden />
      </button>
    </Badge>
  );
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

  const showTypeChip = typeFilterValue !== "all";
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
        "p-4 rounded-xl border border-border/50 bg-card flex flex-col gap-3 animate-fade-in-up",
        containerClassName
      )}
    >
      {/* Ligne principale : recherche | Plus de filtres */}
      <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:gap-3">
        <div className="relative min-w-0 flex-1">
          <Search
            className="absolute left-2.5 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground"
            aria-hidden
          />
          <Input
            type="search"
            placeholder={labels.searchPlaceholder}
            value={searchQuery}
            onChange={(e) => {
              onSearchChange(e.target.value);
              onSearchPageReset();
            }}
            className="h-11 min-h-[44px] pl-9"
            aria-label={labels.searchAriaLabel}
          />
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <Button
            type="button"
            id={`${baseId}-filter-toggle`}
            variant="outline"
            className="h-11 min-h-[44px] gap-1.5 px-3"
            aria-expanded={panelOpen}
            aria-controls={panelId}
            aria-label={filterToggleAriaLabel}
            onClick={() => onPanelOpenChange(!panelOpen)}
          >
            <Filter className="h-4 w-4 shrink-0 text-primary" aria-hidden />
            <span>{labels.filterButton}</span>
            {advancedActiveCount > 0 ? (
              <Badge variant="secondary" className="h-5 min-w-5 px-1 text-[10px] tabular-nums">
                {advancedActiveCount}
              </Badge>
            ) : null}
            <ChevronDown
              className={cn(
                "h-4 w-4 shrink-0 text-muted-foreground transition-transform duration-200",
                panelOpen && "rotate-180"
              )}
              aria-hidden
            />
          </Button>
        </div>
      </div>

      {/* Chips type inline — accès direct, icône + label, 1 clic (NI/enfant) */}
      {showTypeChipsInline && (
        <div
          className="flex flex-wrap items-center gap-1.5"
          role="group"
          aria-label={labels.typeHeading}
        >
          {/* Chip "Tous" — texte explicite, pas d'icône ambiguë */}
          <button
            type="button"
            onClick={() => {
              onTypeFilterChange("all");
              onFilterAdjust();
            }}
            className={cn(
              "inline-flex items-center gap-1.5 rounded-full border px-3 py-1.5 text-xs font-medium transition-colors",
              "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-1",
              typeFilterValue === "all"
                ? "bg-primary text-primary-foreground border-primary"
                : "bg-card border-border/60 text-foreground hover:border-primary/50 hover:bg-primary/5"
            )}
            aria-pressed={typeFilterValue === "all"}
          >
            {labels.allTypes}
          </button>

          {/* Chips par type — icône + label visible, pas de Tooltip nécessaire */}
          {Object.entries(typeStyles).map(([typeKey, { icon: Icon }]) => {
            const label = getTypeDisplay(typeKey);
            const isActive = typeFilterValue === typeKey;
            return (
              <button
                key={typeKey}
                type="button"
                onClick={() => {
                  onTypeFilterChange(typeKey);
                  onFilterAdjust();
                }}
                className={cn(
                  "inline-flex items-center gap-1.5 rounded-full border px-3 py-1.5 text-xs font-medium transition-colors",
                  "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-1",
                  isActive
                    ? "bg-primary text-primary-foreground border-primary"
                    : "bg-card border-border/60 text-foreground hover:border-primary/50 hover:bg-primary/5"
                )}
                aria-pressed={isActive}
                aria-label={label}
              >
                <Icon className="h-3.5 w-3.5 shrink-0" aria-hidden />
                <span>{label}</span>
              </button>
            );
          })}
        </div>
      )}

      {/* Résumé état ordre/masqués : visible panneau fermé, évite l'opacité du badge seul */}
      {showStateSummary && (
        <p className="text-xs text-muted-foreground/70 -mt-1" aria-live="polite">
          {stateSummaryParts.join(" · ")}
        </p>
      )}

      {/* Résumé compact (visible panneau fermé ou ouvert) */}
      {hasSummaryChips ? (
        <div
          className="flex flex-wrap items-center gap-2 border-t border-border/40 pt-2"
          role="group"
          aria-label={labels.activeFiltersSummary}
        >
          {showTypeChip ? (
            <FilterSummaryChip
              label={getTypeDisplay(typeFilterValue)}
              onRemove={onClearTypeFilter}
              removeAriaLabel={labels.removeTypeChip}
            />
          ) : null}
          {showAgeChip ? (
            <FilterSummaryChip
              label={getAgeDisplay(ageFilterValue)}
              onRemove={onClearAgeFilter}
              removeAriaLabel={labels.removeAgeChip}
            />
          ) : null}
        </div>
      ) : null}

      {/* Panneau secondaire : types, âge, reset */}
      <div
        id={panelId}
        role="region"
        aria-labelledby={regionTitleId}
        hidden={!panelOpen}
        className="border-t border-border/60 pt-3 space-y-4"
      >
        <h2 id={regionTitleId} className="sr-only">
          {labels.advancedRegionLabel}
        </h2>

        {/* Filtres par type dans le panneau — seulement si non exposés en inline */}
        {!showTypeChipsInline && (
          <div className="space-y-2">
            <p className="text-xs font-medium text-muted-foreground">{labels.typeHeading}</p>
            <TooltipProvider delayDuration={300}>
              <div className="flex flex-wrap items-center gap-1.5">
                <Tooltip>
                  <TooltipTrigger asChild>
                    <Button
                      type="button"
                      variant={typeFilterValue === "all" ? "default" : "outline"}
                      size="sm"
                      className="h-11 min-h-[44px] min-w-[44px] p-0"
                      onClick={() => {
                        onTypeFilterChange("all");
                        onFilterAdjust();
                      }}
                    >
                      <Filter className="h-4 w-4" aria-hidden />
                    </Button>
                  </TooltipTrigger>
                  <TooltipContent side="bottom">{labels.allTypes}</TooltipContent>
                </Tooltip>
                <div
                  className="mx-0.5 hidden h-11 w-px shrink-0 self-center bg-border sm:block"
                  aria-hidden
                />
                {Object.entries(typeStyles).map(([typeKey, { icon: Icon }]) => (
                  <Tooltip key={typeKey}>
                    <TooltipTrigger asChild>
                      <Button
                        type="button"
                        variant={typeFilterValue === typeKey ? "default" : "outline"}
                        size="sm"
                        className="h-11 min-h-[44px] min-w-[44px] p-0"
                        onClick={() => {
                          onTypeFilterChange(typeKey);
                          onFilterAdjust();
                        }}
                      >
                        <Icon className="h-4 w-4" aria-hidden />
                      </Button>
                    </TooltipTrigger>
                    <TooltipContent side="bottom">{getTypeDisplay(typeKey)}</TooltipContent>
                  </Tooltip>
                ))}
              </div>
            </TooltipProvider>
          </div>
        )}

        <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:flex-wrap">
          <div className="space-y-1.5 min-w-0 sm:max-w-xs">
            <label htmlFor={`${baseId}-age`} className="text-xs font-medium text-muted-foreground">
              {labels.ageGroup}
            </label>
            <Select
              value={ageFilterValue}
              onValueChange={(value) => {
                onAgeFilterChange(value);
                onFilterAdjust();
              }}
            >
              <SelectTrigger id={`${baseId}-age`} className="h-11 min-h-[44px] w-full sm:w-[200px]">
                <SelectValue placeholder={labels.allAgesPlaceholder} />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">{labels.allAgesPlaceholder}</SelectItem>
                {ageGroupValues.map((value) => (
                  <SelectItem key={value} value={value}>
                    {getAgeDisplay(value)}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-1.5 min-w-0">
            <label
              htmlFor={`${baseId}-order`}
              className="text-xs font-medium text-muted-foreground"
            >
              {labels.orderLabel}
            </label>
            <Select
              value={orderValue}
              onValueChange={(value) => {
                onOrderChange(value as ContentListOrder);
                onFilterAdjust();
              }}
            >
              <SelectTrigger
                id={`${baseId}-order`}
                className="h-11 min-h-[44px] w-full sm:w-[160px]"
                aria-label={labels.orderAria}
              >
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value={CONTENT_LIST_ORDER.RANDOM}>{labels.orderRandom}</SelectItem>
                <SelectItem value={CONTENT_LIST_ORDER.RECENT}>{labels.orderRecent}</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <label
            htmlFor={hideCompletedFieldId}
            className="flex min-h-[44px] cursor-pointer items-center gap-2 text-xs text-muted-foreground self-end"
          >
            <Switch
              id={hideCompletedFieldId}
              checked={hideCompleted}
              onCheckedChange={(checked) => {
                onHideCompletedChange(checked);
                onFilterAdjust();
              }}
            />
            <span>{labels.hideCompleted}</span>
          </label>
        </div>

        <div className="flex justify-end">
          {hasResettableState ? (
            <Button
              type="button"
              variant="ghost"
              className="h-11 min-h-[44px] shrink-0 text-muted-foreground hover:text-foreground"
              onClick={onResetAll}
            >
              <X className="mr-1 h-4 w-4" aria-hidden />
              {labels.reset}
            </Button>
          ) : null}
        </div>
      </div>
    </div>
  );
}
