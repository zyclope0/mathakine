"use client";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { Loader2, X } from "lucide-react";

/** Compact streaming strip (compact base, unified IA zone, card mode). */
export function AIGeneratorStreamingRow({
  streamedText,
  fallbackLabel,
  cancelLabel,
  onCancel,
  rootClassName,
  streamParagraphClassName,
  cancelButtonClassName,
}: {
  streamedText: string;
  fallbackLabel: string;
  cancelLabel: string;
  onCancel: () => void;
  rootClassName?: string;
  streamParagraphClassName?: string;
  cancelButtonClassName?: string;
}) {
  return (
    <div
      className={cn(
        "rounded-lg bg-card/60 border border-border/50 flex items-center gap-2",
        rootClassName
      )}
    >
      <Loader2 className="h-4 w-4 animate-spin text-primary flex-shrink-0" aria-hidden="true" />
      <p className={cn("flex-1 text-xs text-muted-foreground", streamParagraphClassName)}>
        {streamedText || fallbackLabel}
      </p>
      <Button
        variant="ghost"
        size="sm"
        onClick={onCancel}
        className={cn("h-6 w-6 p-0", cancelButtonClassName)}
        aria-label={cancelLabel}
      >
        <X className="h-3 w-3" aria-hidden="true" />
      </Button>
    </div>
  );
}

/** Horizontal success strip used in compact generator layouts. */
export function AIGeneratorSuccessRowCompact({
  successLabel,
  title,
  viewItemLabel,
  onViewItem,
  showViewButton,
  onDismiss,
  closeAriaLabel,
  rootClassName,
}: {
  successLabel: string;
  title: string;
  viewItemLabel: string;
  onViewItem: () => void;
  showViewButton: boolean;
  onDismiss: () => void;
  closeAriaLabel: string;
  rootClassName?: string;
}) {
  return (
    <div
      className={cn(
        "rounded-lg bg-success/10 border border-success/20 flex items-center justify-between gap-3",
        rootClassName
      )}
    >
      <div className="flex-1 min-w-0">
        <p className="text-xs font-medium text-success mb-0.5">{successLabel}</p>
        <p className="text-sm text-foreground truncate">{title}</p>
      </div>
      <div className="flex items-center gap-2 flex-shrink-0">
        {showViewButton ? (
          <Button size="sm" variant="outline" onClick={onViewItem} className="h-7 text-xs">
            {viewItemLabel}
          </Button>
        ) : null}
        <Button
          variant="ghost"
          size="sm"
          onClick={onDismiss}
          className="h-7 w-7 p-0"
          aria-label={closeAriaLabel}
        >
          <X className="h-3.5 w-3.5" aria-hidden="true" />
        </Button>
      </div>
    </div>
  );
}
