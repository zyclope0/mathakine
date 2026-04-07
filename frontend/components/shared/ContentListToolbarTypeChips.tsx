"use client";

import { cn } from "@/lib/utils";
import type { TypeStyleMap } from "@/components/shared/contentListToolbarTypes";

const INLINE_CHIP_BASE =
  "inline-flex items-center gap-1.5 rounded-full border px-3 py-1.5 text-xs font-medium " +
  "transition-colors active:scale-95 touch-manipulation " +
  "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-1";

const INLINE_CHIP_ACTIVE = "bg-primary text-primary-foreground border-primary";
const INLINE_CHIP_IDLE =
  "bg-card border-border/60 text-foreground hover:border-primary/50 hover:bg-primary/5";

export interface ContentListToolbarTypeChipsProps {
  typeHeadingAriaLabel: string;
  allTypesLabel: string;
  typeFilterValue: string;
  onTypeFilterChange: (value: string) => void;
  onFilterAdjust: () => void;
  typeStyles: TypeStyleMap;
  getTypeDisplay: (typeKey: string) => string;
}

export function ContentListToolbarTypeChips({
  typeHeadingAriaLabel,
  allTypesLabel,
  typeFilterValue,
  onTypeFilterChange,
  onFilterAdjust,
  typeStyles,
  getTypeDisplay,
}: ContentListToolbarTypeChipsProps) {
  return (
    <div
      className="flex flex-wrap items-center gap-2"
      role="group"
      aria-label={typeHeadingAriaLabel}
    >
      <button
        type="button"
        onClick={() => {
          onTypeFilterChange("all");
          onFilterAdjust();
        }}
        className={cn(
          INLINE_CHIP_BASE,
          typeFilterValue === "all" ? INLINE_CHIP_ACTIVE : INLINE_CHIP_IDLE
        )}
        aria-pressed={typeFilterValue === "all"}
      >
        {allTypesLabel}
      </button>

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
            className={cn(INLINE_CHIP_BASE, isActive ? INLINE_CHIP_ACTIVE : INLINE_CHIP_IDLE)}
            aria-pressed={isActive}
            aria-label={label}
          >
            <Icon className="h-3.5 w-3.5 shrink-0" aria-hidden />
            <span>{label}</span>
          </button>
        );
      })}
    </div>
  );
}
