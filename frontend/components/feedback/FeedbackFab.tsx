"use client";

import { useState, useRef, useEffect, useMemo } from "react";
import { usePathname } from "next/navigation";
import { Flag, MessageCircle, AlertTriangle, Bug, FileQuestion } from "lucide-react";
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
import { toast } from "sonner";
import { api } from "@/lib/api/client";
import { cn } from "@/lib/utils/cn";

const FEEDBACK_EMAIL =
  process.env.NEXT_PUBLIC_FEEDBACK_EMAIL || "webmaster@mathakine.fun";

export type FeedbackContext = {
  exerciseId?: number;
  challengeId?: number;
};

interface FeedbackFabProps {
  context?: FeedbackContext;
  className?: string;
}

const FEEDBACK_TYPES = [
  { id: "exercise", icon: FileQuestion, subjectKey: "exerciseSubject" },
  { id: "challenge", icon: AlertTriangle, subjectKey: "challengeSubject" },
  { id: "ui", icon: Bug, subjectKey: "uiSubject" },
  { id: "other", icon: MessageCircle, subjectKey: "otherSubject" },
] as const;

type FeedbackTypeId = (typeof FEEDBACK_TYPES)[number]["id"];

export function FeedbackFab({ context: contextProp, className }: FeedbackFabProps) {
  const t = useTranslations("feedback.fab");
  const pathname = usePathname();
  const [isOpen, setIsOpen] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [selectedType, setSelectedType] = useState<FeedbackTypeId | null>(null);
  const [description, setDescription] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const context = useMemo(() => {
    if (contextProp) return contextProp;
    const exerciseMatch = pathname.match(/\/exercises\/(\d+)/);
    const challengeMatch = pathname.match(/\/challenge\/(\d+)/);
    return {
      ...(exerciseMatch && { exerciseId: parseInt(exerciseMatch[1], 10) }),
      ...(challengeMatch && { challengeId: parseInt(challengeMatch[1], 10) }),
    };
  }, [pathname, contextProp]);

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const getTypeLabel = (id: FeedbackTypeId) => {
    const labels: Record<FeedbackTypeId, string> = {
      exercise: t("typeExercise", { default: "Exercice incorrect" }),
      challenge: t("typeChallenge", { default: "Défi incorrect" }),
      ui: t("typeUi", { default: "Bug graphique" }),
      other: t("typeOther", { default: "Autre" }),
    };
    return labels[id];
  };

  const handleSelect = (type: FeedbackTypeId) => {
    setSelectedType(type);
    setDescription("");
    setModalOpen(true);
    setIsOpen(false);
  };

  const handleSubmit = async () => {
    if (!selectedType) return;
    setIsSubmitting(true);
    try {
      const payload = {
        feedback_type: selectedType,
        description: description.trim() || undefined,
        page_url: typeof window !== "undefined" ? window.location.href : pathname,
        exercise_id: context?.exerciseId ?? undefined,
        challenge_id: context?.challengeId ?? undefined,
      };
      await api.post<{ success: boolean; id: number }>("/api/feedback", payload);
      toast.success(t("successMessage", { default: "Merci pour votre retour !" }));
      setModalOpen(false);
      setSelectedType(null);
      setDescription("");
    } catch (err) {
      toast.error(t("errorMessage", { default: "Erreur lors de l'envoi." }));
      // Fallback mailto si l'API échoue
      const subjects: Record<string, string> = {
        exercise: t("exerciseSubject", { default: "Exercice incorrect ou incohérent" }),
        challenge: t("challengeSubject", { default: "Défi incorrect ou incohérent" }),
        ui: t("uiSubject", { default: "Bug graphique / interface" }),
        other: t("otherSubject", { default: "Autre signalement" }),
      };
      const subject = encodeURIComponent(`[Alpha] ${subjects[selectedType]}`);
      const lines = [
        `Page: ${typeof window !== "undefined" ? window.location.href : pathname}`,
        ...(context?.exerciseId ? [`Exercice ID: ${context.exerciseId}`] : []),
        ...(context?.challengeId ? [`Défi ID: ${context.challengeId}`] : []),
        "",
        description.trim() || t("bodyPlaceholder", { default: "Décrivez le problème ici :" }),
      ];
      const body = encodeURIComponent(lines.join("\n"));
      window.open(`mailto:${FEEDBACK_EMAIL}?subject=${subject}&body=${body}`, "_blank");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <>
      <div ref={dropdownRef} className={cn("fixed bottom-6 right-6 z-40", className)}>
        <div
          className={cn(
            "absolute bottom-14 right-0 mb-2 flex flex-col gap-1 rounded-lg border bg-card p-1 shadow-lg transition-opacity",
            isOpen ? "opacity-100" : "pointer-events-none opacity-0"
          )}
        >
          {FEEDBACK_TYPES.map(({ id, icon: Icon }) => (
            <Button
              key={id}
              variant="ghost"
              size="sm"
              className="justify-start gap-2"
              onClick={() => handleSelect(id)}
            >
              <Icon className="h-4 w-4" />
              {getTypeLabel(id)}
            </Button>
          ))}
        </div>
        <Button
          variant="default"
          size="icon"
          className="h-12 w-12 rounded-full shadow-lg bg-[#FFCCCC] hover:bg-[#FFB3B3] text-[#C00030]"
          onClick={() => setIsOpen(!isOpen)}
          aria-label={t("buttonLabel", { default: "Signaler un problème" })}
          aria-expanded={isOpen}
        >
          <Flag className="h-5 w-5" />
        </Button>
      </div>

      <Dialog open={modalOpen} onOpenChange={setModalOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              {selectedType ? getTypeLabel(selectedType) : t("buttonLabel")}
            </DialogTitle>
            <DialogDescription>
              {t("modalDescription", {
                default: "Décrivez le problème. Votre retour sera visible dans l'admin.",
              })}
            </DialogDescription>
          </DialogHeader>
          <Textarea
            placeholder={t("bodyPlaceholder", { default: "Décrivez le problème ici..." })}
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className="min-h-[120px]"
            disabled={isSubmitting}
          />
          <DialogFooter>
            <Button variant="outline" onClick={() => setModalOpen(false)} disabled={isSubmitting}>
              {t("cancel", { default: "Annuler" })}
            </Button>
            <Button onClick={handleSubmit} disabled={isSubmitting}>
              {isSubmitting
                ? t("sending", { default: "Envoi..." })
                : t("send", { default: "Envoyer" })}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}
