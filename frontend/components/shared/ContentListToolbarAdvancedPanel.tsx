"use client";

import { Filter, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { CONTENT_LIST_ORDER, type ContentListOrder } from "@/lib/constants/contentListOrder";
import type { TypeStyleMap } from "@/components/shared/contentListToolbarTypes";

export interface ContentListToolbarAdvancedPanelProps {
  panelId: string;
  regionTitleId: string;
  panelOpen: boolean;
  advancedRegionLabel: string;
  showTypeChipsInline: boolean;
  typeHeading: string;
  allTypesLabel: string;
  typeFilterValue: string;
  onTypeFilterChange: (value: string) => void;
  onFilterAdjust: () => void;
  typeStyles: TypeStyleMap;
  getTypeDisplay: (typeKey: string) => string;
  ageFieldId: string;
  ageGroupLabel: string;
  allAgesPlaceholder: string;
  ageFilterValue: string;
  onAgeFilterChange: (value: string) => void;
  ageGroupValues: readonly string[];
  getAgeDisplay: (ageKey: string) => string;
  orderFieldId: string;
  orderLabel: string;
  orderAria: string;
  orderRandom: string;
  orderRecent: string;
  orderValue: ContentListOrder;
  onOrderChange: (value: ContentListOrder) => void;
  hideCompletedFieldId: string;
  hideCompleted: boolean;
  onHideCompletedChange: (checked: boolean) => void;
  hideCompletedLabel: string;
  hasResettableState: boolean;
  resetLabel: string;
  onResetAll: () => void;
}

export function ContentListToolbarAdvancedPanel({
  panelId,
  regionTitleId,
  panelOpen,
  advancedRegionLabel,
  showTypeChipsInline,
  typeHeading,
  allTypesLabel,
  typeFilterValue,
  onTypeFilterChange,
  onFilterAdjust,
  typeStyles,
  getTypeDisplay,
  ageFieldId,
  ageGroupLabel,
  allAgesPlaceholder,
  ageFilterValue,
  onAgeFilterChange,
  ageGroupValues,
  getAgeDisplay,
  orderFieldId,
  orderLabel,
  orderAria,
  orderRandom,
  orderRecent,
  orderValue,
  onOrderChange,
  hideCompletedFieldId,
  hideCompleted,
  onHideCompletedChange,
  hideCompletedLabel,
  hasResettableState,
  resetLabel,
  onResetAll,
}: ContentListToolbarAdvancedPanelProps) {
  return (
    <div
      id={panelId}
      role="region"
      aria-labelledby={regionTitleId}
      hidden={!panelOpen}
      className="border-t border-border/60 pt-3 space-y-3"
    >
      <h2 id={regionTitleId} className="sr-only">
        {advancedRegionLabel}
      </h2>

      {!showTypeChipsInline ? (
        <div className="space-y-2">
          <p className="text-xs font-medium text-muted-foreground">{typeHeading}</p>
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
                <TooltipContent side="bottom">{allTypesLabel}</TooltipContent>
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
      ) : null}

      <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:flex-wrap">
        <div className="space-y-1.5 min-w-0 sm:max-w-xs">
          <label htmlFor={ageFieldId} className="text-xs font-medium text-muted-foreground">
            {ageGroupLabel}
          </label>
          <Select
            value={ageFilterValue}
            onValueChange={(value) => {
              onAgeFilterChange(value);
              onFilterAdjust();
            }}
          >
            <SelectTrigger id={ageFieldId} className="h-11 min-h-[44px] w-full sm:w-[200px]">
              <SelectValue placeholder={allAgesPlaceholder} />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">{allAgesPlaceholder}</SelectItem>
              {ageGroupValues.map((value) => (
                <SelectItem key={value} value={value}>
                  {getAgeDisplay(value)}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-1.5 min-w-0">
          <label htmlFor={orderFieldId} className="text-xs font-medium text-muted-foreground">
            {orderLabel}
          </label>
          <Select
            value={orderValue}
            onValueChange={(value) => {
              onOrderChange(value as ContentListOrder);
              onFilterAdjust();
            }}
          >
            <SelectTrigger
              id={orderFieldId}
              className="h-11 min-h-[44px] w-full sm:w-[160px]"
              aria-label={orderAria}
            >
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value={CONTENT_LIST_ORDER.RANDOM}>{orderRandom}</SelectItem>
              <SelectItem value={CONTENT_LIST_ORDER.RECENT}>{orderRecent}</SelectItem>
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
          <span>{hideCompletedLabel}</span>
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
            {resetLabel}
          </Button>
        ) : null}
      </div>
    </div>
  );
}
