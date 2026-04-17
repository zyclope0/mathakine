"use client";

import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { useTranslations } from "next-intl";
import type { FeedbackTypeId } from "@/components/feedback/feedbackConfig";

export interface FeedbackComposerProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  selectedType: FeedbackTypeId | null;
  description: string;
  onDescriptionChange: (value: string) => void;
  isSubmitting: boolean;
  onSubmit: () => void;
  getTypeLabel: (id: FeedbackTypeId) => string;
}

/**
 * Shared feedback description modal (API + mailto fallback live in useFeedbackFlow).
 */
export function FeedbackComposer({
  open,
  onOpenChange,
  selectedType,
  description,
  onDescriptionChange,
  isSubmitting,
  onSubmit,
  getTypeLabel,
}: FeedbackComposerProps) {
  const t = useTranslations("feedback.fab");

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{selectedType ? getTypeLabel(selectedType) : t("buttonLabel")}</DialogTitle>
          <DialogDescription>
            {t("modalDescription", {
              default: "Décrivez le problème. Votre retour sera visible dans l'admin.",
            })}
          </DialogDescription>
        </DialogHeader>
        <Textarea
          placeholder={t("bodyPlaceholder", { default: "Décrivez le problème ici..." })}
          value={description}
          onChange={(e) => onDescriptionChange(e.target.value)}
          className="min-h-[120px]"
          disabled={isSubmitting}
        />
        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)} disabled={isSubmitting}>
            {t("cancel", { default: "Annuler" })}
          </Button>
          <Button onClick={() => void onSubmit()} disabled={isSubmitting}>
            {isSubmitting
              ? t("sending", { default: "Envoi..." })
              : t("send", { default: "Envoyer" })}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
