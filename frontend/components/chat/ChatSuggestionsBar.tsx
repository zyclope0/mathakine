"use client";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

export type ChatSuggestionsLayoutVariant = "embedded" | "drawer";

export interface ChatSuggestionsBarProps {
  visible: boolean;
  variant: ChatSuggestionsLayoutVariant;
  suggestions: string[];
  suggestionsTitle: string;
  onPick: (text: string) => void;
  disabled: boolean;
}

export function ChatSuggestionsBar({
  visible,
  variant,
  suggestions,
  suggestionsTitle,
  onPick,
  disabled,
}: ChatSuggestionsBarProps) {
  if (!visible || suggestions.length === 0) return null;

  const isDrawer = variant === "drawer";

  return (
    <div className={cn(isDrawer ? "border-t px-4 pb-3 pt-3" : "border-t p-4")}>
      {isDrawer ? (
        <p className="mb-2 text-xs text-muted-foreground">{suggestionsTitle}</p>
      ) : (
        <h4 className="mb-2 text-sm font-semibold text-muted-foreground">{suggestionsTitle}</h4>
      )}
      <div className="flex flex-wrap gap-2">
        {suggestions.map((s, i) => (
          <Button
            key={i}
            variant="outline"
            size="sm"
            type="button"
            disabled={disabled}
            onClick={() => onPick(s)}
            className={cn("text-xs", isDrawer && "h-8 rounded-full")}
          >
            {s}
          </Button>
        ))}
      </div>
    </div>
  );
}
