"use client";

import { X } from "lucide-react";
import { Badge } from "@/components/ui/badge";

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

export interface ContentListToolbarSummaryProps {
  showStateSummary: boolean;
  stateSummaryText: string;
  hasSummaryChips: boolean;
  activeFiltersSummaryAriaLabel: string;
  showTypeChip: boolean;
  typeChipLabel: string;
  onClearTypeFilter: () => void;
  removeTypeChipAriaLabel: string;
  showAgeChip: boolean;
  ageChipLabel: string;
  onClearAgeFilter: () => void;
  removeAgeChipAriaLabel: string;
}

export function ContentListToolbarSummary({
  showStateSummary,
  stateSummaryText,
  hasSummaryChips,
  activeFiltersSummaryAriaLabel,
  showTypeChip,
  typeChipLabel,
  onClearTypeFilter,
  removeTypeChipAriaLabel,
  showAgeChip,
  ageChipLabel,
  onClearAgeFilter,
  removeAgeChipAriaLabel,
}: ContentListToolbarSummaryProps) {
  return (
    <>
      {showStateSummary ? (
        <p className="text-xs text-muted-foreground/70 -mt-1" aria-live="polite">
          {stateSummaryText}
        </p>
      ) : null}

      {hasSummaryChips ? (
        <div
          className="flex flex-wrap items-center gap-2 border-t border-border/40 pt-2"
          role="group"
          aria-label={activeFiltersSummaryAriaLabel}
        >
          {showTypeChip ? (
            <FilterSummaryChip
              label={typeChipLabel}
              onRemove={onClearTypeFilter}
              removeAriaLabel={removeTypeChipAriaLabel}
            />
          ) : null}
          {showAgeChip ? (
            <FilterSummaryChip
              label={ageChipLabel}
              onRemove={onClearAgeFilter}
              removeAriaLabel={removeAgeChipAriaLabel}
            />
          ) : null}
        </div>
      ) : null}
    </>
  );
}
