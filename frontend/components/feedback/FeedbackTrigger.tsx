"use client";

import { Flag } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useTranslations } from "next-intl";
import { cn } from "@/lib/utils";
import { FeedbackComposer } from "@/components/feedback/FeedbackComposer";
import { useFeedbackFlow } from "@/components/feedback/useFeedbackFlow";
import { FEEDBACK_TYPES, type FeedbackContext } from "@/components/feedback/feedbackConfig";

export type FeedbackTriggerVariant = "ghost" | "outline" | "subtle";

export type FeedbackTriggerLayout = "icon" | "icon-label";

export interface FeedbackTriggerProps {
  componentId?: string;
  context?: FeedbackContext;
  variant?: FeedbackTriggerVariant;
  layout?: FeedbackTriggerLayout;
  className?: string;
}

/**
 * Inline / contextual entry to the same feedback type picker + composer as {@link FeedbackFab}.
 * Does not render a fixed-position FAB — use for header, post-result tools, etc.
 */
export function FeedbackTrigger({
  componentId,
  context,
  variant = "ghost",
  layout = "icon",
  className,
}: FeedbackTriggerProps) {
  const t = useTranslations("feedback.fab");
  const flow = useFeedbackFlow({
    ...(context !== undefined ? { context } : {}),
    ...(componentId !== undefined ? { componentId } : {}),
  });

  const buttonVariant = variant === "outline" ? "outline" : "ghost";
  const subtleTone =
    variant === "subtle" ? "text-muted-foreground hover:text-foreground" : undefined;

  return (
    <>
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button
            type="button"
            variant={buttonVariant}
            size={layout === "icon" ? "icon" : "sm"}
            className={cn(
              layout === "icon" && "h-9 w-9 shrink-0",
              layout === "icon-label" && "gap-1.5 px-2.5 text-xs font-medium",
              subtleTone,
              className
            )}
            aria-label={t("buttonLabel", { default: "Signaler un problème" })}
            aria-haspopup="menu"
          >
            <Flag
              className={cn("shrink-0", layout === "icon" ? "h-4 w-4" : "h-3.5 w-3.5")}
              aria-hidden
            />
            {layout === "icon-label" ? (
              <span className="max-w-[10rem] truncate">{t("inlineTriggerLabel")}</span>
            ) : null}
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end" className="w-56">
          {FEEDBACK_TYPES.map(({ id, icon: Icon }) => (
            <DropdownMenuItem
              key={id}
              className="gap-2"
              onSelect={() => {
                flow.openModalForType(id);
              }}
            >
              <Icon className="h-4 w-4 shrink-0" aria-hidden />
              {flow.getTypeLabel(id)}
            </DropdownMenuItem>
          ))}
        </DropdownMenuContent>
      </DropdownMenu>

      <FeedbackComposer
        open={flow.modalOpen}
        onOpenChange={flow.setModalOpen}
        selectedType={flow.selectedType}
        description={flow.description}
        onDescriptionChange={flow.setDescription}
        isSubmitting={flow.isSubmitting}
        onSubmit={flow.handleSubmit}
        getTypeLabel={flow.getTypeLabel}
      />
    </>
  );
}

export type { FeedbackContext };
