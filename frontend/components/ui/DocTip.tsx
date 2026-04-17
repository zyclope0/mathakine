"use client";

import { HelpCircle } from "lucide-react";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import { cn } from "@/lib/utils";

export interface DocTipProps {
  label: string;
  side?: "top" | "right" | "bottom" | "left";
  className?: string;
}

/**
 * Compact contextual help icon with tooltip (docs / micro-guidage).
 */
export function DocTip({ label, side = "top", className }: DocTipProps) {
  return (
    <span className={cn("inline-flex items-center", className)}>
      <Tooltip>
        <TooltipTrigger
          type="button"
          className="inline-flex shrink-0 rounded-sm text-muted-foreground/60 hover:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background"
          aria-label={label}
        >
          <HelpCircle className="h-3.5 w-3.5" aria-hidden />
        </TooltipTrigger>
        <TooltipContent side={side} className="z-[100010] max-w-[220px] text-xs whitespace-normal">
          {label}
        </TooltipContent>
      </Tooltip>
    </span>
  );
}
