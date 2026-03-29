"use client";

import { Button } from "@/components/ui/button";
import { LayoutGrid, List } from "lucide-react";
import type { ContentListViewMode } from "@/lib/contentList/viewMode";

interface ContentListViewModeToggleProps {
  viewMode: ContentListViewMode;
  onViewModeChange: (mode: ContentListViewMode) => void;
  ariaLabelGrid: string;
  ariaLabelList: string;
}

export function ContentListViewModeToggle({
  viewMode,
  onViewModeChange,
  ariaLabelGrid,
  ariaLabelList,
}: ContentListViewModeToggleProps) {
  return (
    <div className="flex items-center gap-1 border rounded-lg p-1 shrink-0">
      <Button
        variant={viewMode === "grid" ? "default" : "ghost"}
        size="sm"
        onClick={() => onViewModeChange("grid")}
        className="h-11 w-11 min-h-[44px] min-w-[44px] p-0"
        aria-label={ariaLabelGrid}
        aria-pressed={viewMode === "grid"}
      >
        <LayoutGrid className="h-4 w-4" aria-hidden="true" />
      </Button>
      <Button
        variant={viewMode === "list" ? "default" : "ghost"}
        size="sm"
        onClick={() => onViewModeChange("list")}
        className="h-11 w-11 min-h-[44px] min-w-[44px] p-0"
        aria-label={ariaLabelList}
        aria-pressed={viewMode === "list"}
      >
        <List className="h-4 w-4" aria-hidden="true" />
      </Button>
    </div>
  );
}
