"use client";

import { useCallback, useMemo, useState } from "react";
import { usePathname } from "next/navigation";
import { useTranslations } from "next-intl";
import { toast } from "sonner";
import { api } from "@/lib/api/client";
import { useAccessibilityStore } from "@/lib/stores/accessibilityStore";
import { useThemeStore } from "@/lib/stores/themeStore";
import { type FeedbackContext, type FeedbackTypeId } from "@/components/feedback/feedbackConfig";

const FEEDBACK_EMAIL = process.env.NEXT_PUBLIC_FEEDBACK_EMAIL || "webmaster@mathakine.fun";

export type UseFeedbackFlowOptions = {
  context?: FeedbackContext;
  componentId?: string;
};

export function useFeedbackFlow(options: UseFeedbackFlowOptions) {
  const { context: contextProp, componentId: componentIdProp } = options;
  const t = useTranslations("feedback.fab");
  const pathname = usePathname();

  const resolvedContext = useMemo((): FeedbackContext => {
    if (contextProp) return contextProp;
    const exerciseMatch = pathname.match(/\/exercises\/(\d+)/);
    const challengeMatch = pathname.match(/\/challenge\/(\d+)/);
    const exerciseId = exerciseMatch?.[1];
    const challengeId = challengeMatch?.[1];
    return {
      ...(exerciseId && { exerciseId: parseInt(exerciseId, 10) }),
      ...(challengeId && { challengeId: parseInt(challengeId, 10) }),
    };
  }, [pathname, contextProp]);

  const activeTheme = useThemeStore((s) => s.theme);
  const { dyslexiaMode, focusMode, reducedMotion, largeText, highContrast } =
    useAccessibilityStore();
  const niState =
    dyslexiaMode || focusMode || reducedMotion || largeText || highContrast ? "on" : "off";

  const [modalOpen, setModalOpen] = useState(false);
  const [selectedType, setSelectedType] = useState<FeedbackTypeId | null>(null);
  const [description, setDescription] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const getTypeLabel = useCallback(
    (id: FeedbackTypeId) => {
      const labels: Record<FeedbackTypeId, string> = {
        exercise: t("typeExercise", { default: "Exercice incorrect" }),
        challenge: t("typeChallenge", { default: "Défi incorrect" }),
        ui: t("typeUi", { default: "Bug graphique" }),
        other: t("typeOther", { default: "Autre" }),
      };
      return labels[id];
    },
    [t]
  );

  const openModalForType = useCallback((type: FeedbackTypeId) => {
    setSelectedType(type);
    setDescription("");
    setModalOpen(true);
  }, []);

  const componentIdResolved = componentIdProp ?? "FeedbackFab";

  const handleSubmit = useCallback(async () => {
    if (!selectedType) return;
    setIsSubmitting(true);
    try {
      const payload = {
        feedback_type: selectedType,
        description: description.trim() || undefined,
        page_url: typeof window !== "undefined" ? window.location.href : pathname,
        exercise_id: resolvedContext.exerciseId ?? undefined,
        challenge_id: resolvedContext.challengeId ?? undefined,
        active_theme: activeTheme,
        ni_state: niState,
        component_id: componentIdResolved,
      };
      await api.post<{ success: boolean; id: number }>("/api/feedback", payload);
      toast.success(t("successMessage", { default: "Merci pour votre retour !" }));
      setModalOpen(false);
      setSelectedType(null);
      setDescription("");
    } catch {
      toast.error(t("errorMessage", { default: "Erreur lors de l'envoi." }));
      const subjects: Record<string, string> = {
        exercise: t("exerciseSubject", { default: "Exercice incorrect ou incohérent" }),
        challenge: t("challengeSubject", { default: "Défi incorrect ou incohérent" }),
        ui: t("uiSubject", { default: "Bug graphique / interface" }),
        other: t("otherSubject", { default: "Autre signalement" }),
      };
      const subject = encodeURIComponent(`[Alpha] ${subjects[selectedType]}`);
      const lines = [
        `Page: ${typeof window !== "undefined" ? window.location.href : pathname}`,
        ...(resolvedContext.exerciseId ? [`Exercice ID: ${resolvedContext.exerciseId}`] : []),
        ...(resolvedContext.challengeId ? [`Défi ID: ${resolvedContext.challengeId}`] : []),
        "",
        description.trim() || t("bodyPlaceholder", { default: "Décrivez le problème ici :" }),
      ];
      const body = encodeURIComponent(lines.join("\n"));
      if (typeof window !== "undefined") {
        window.open(`mailto:${FEEDBACK_EMAIL}?subject=${subject}&body=${body}`, "_blank");
      }
    } finally {
      setIsSubmitting(false);
    }
  }, [
    activeTheme,
    description,
    niState,
    pathname,
    resolvedContext.challengeId,
    resolvedContext.exerciseId,
    selectedType,
    t,
    componentIdResolved,
  ]);

  return {
    resolvedContext,
    modalOpen,
    setModalOpen,
    selectedType,
    description,
    setDescription,
    isSubmitting,
    openModalForType,
    handleSubmit,
    getTypeLabel,
    componentIdResolved,
  };
}
