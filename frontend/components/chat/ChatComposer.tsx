"use client";

import type { KeyboardEvent, RefObject } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Send, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";

export type ChatComposerLayoutVariant = "embedded" | "drawer";

export interface ChatComposerProps {
  variant: ChatComposerLayoutVariant;
  inputRef: RefObject<HTMLInputElement | null>;
  value: string;
  onChange: (value: string) => void;
  onKeyDown: (e: KeyboardEvent<HTMLInputElement>) => void;
  onSend: () => void;
  disabled: boolean;
  canSend: boolean;
  placeholder: string;
  inputAriaLabel: string;
  sendAriaLabel: string;
  /** Texte d’aide sous le champ (embedded uniquement). */
  footerHint?: string;
}

export function ChatComposer({
  variant,
  inputRef,
  value,
  onChange,
  onKeyDown,
  onSend,
  disabled,
  canSend,
  placeholder,
  inputAriaLabel,
  sendAriaLabel,
  footerHint,
}: ChatComposerProps) {
  const isDrawer = variant === "drawer";

  return (
    <div className="border-t bg-background p-4">
      <div className="flex gap-2">
        <Input
          ref={inputRef}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onKeyDown={onKeyDown}
          placeholder={placeholder}
          disabled={disabled}
          className={cn("flex-1", isDrawer && "rounded-full bg-muted/50 px-4 py-3")}
          aria-label={inputAriaLabel}
        />
        <Button
          type="button"
          onClick={onSend}
          disabled={!canSend || disabled}
          size="icon"
          className={cn(isDrawer && "h-11 w-11 rounded-full")}
          aria-label={sendAriaLabel}
        >
          {disabled ? (
            <Loader2 className={cn("animate-spin", isDrawer ? "h-5 w-5" : "h-4 w-4")} />
          ) : (
            <Send className={cn(isDrawer ? "h-5 w-5" : "h-4 w-4")} />
          )}
        </Button>
      </div>
      {!isDrawer && footerHint ? (
        <p className="mt-2 text-xs text-muted-foreground">{footerHint}</p>
      ) : null}
    </div>
  );
}
