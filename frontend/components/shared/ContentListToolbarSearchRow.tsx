"use client";

import { ChevronDown, Filter, Search } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

export interface ContentListToolbarSearchRowProps {
  searchPlaceholder: string;
  searchAriaLabel: string;
  searchQuery: string;
  onSearchChange: (value: string) => void;
  onSearchPageReset: () => void;
  filterButtonLabel: string;
  filterToggleAriaLabel: string;
  filterToggleId: string;
  panelOpen: boolean;
  onPanelOpenChange: (open: boolean) => void;
  panelId: string;
  advancedActiveCount: number;
}

export function ContentListToolbarSearchRow({
  searchPlaceholder,
  searchAriaLabel,
  searchQuery,
  onSearchChange,
  onSearchPageReset,
  filterButtonLabel,
  filterToggleAriaLabel,
  filterToggleId,
  panelOpen,
  onPanelOpenChange,
  panelId,
  advancedActiveCount,
}: ContentListToolbarSearchRowProps) {
  return (
    <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:gap-3">
      <div className="relative min-w-0 flex-1">
        <Search
          className="absolute left-2.5 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground"
          aria-hidden
        />
        <Input
          type="search"
          placeholder={searchPlaceholder}
          value={searchQuery}
          onChange={(e) => {
            onSearchChange(e.target.value);
            onSearchPageReset();
          }}
          className="h-11 min-h-[44px] pl-9"
          aria-label={searchAriaLabel}
        />
      </div>

      <div className="flex flex-wrap items-center gap-2">
        <Button
          type="button"
          id={filterToggleId}
          variant="outline"
          className="h-11 min-h-[44px] gap-1.5 px-3"
          aria-expanded={panelOpen}
          aria-controls={panelId}
          aria-label={filterToggleAriaLabel}
          onClick={() => onPanelOpenChange(!panelOpen)}
        >
          <Filter className="h-4 w-4 shrink-0 text-primary" aria-hidden />
          <span>{filterButtonLabel}</span>
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
  );
}
