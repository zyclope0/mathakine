import { toast } from "sonner";
import type { Exercise } from "@/types/api";
import type { AiGenerationSseTranslate } from "@/lib/ai/generation/types";
import { normalizeCreatedResourceId } from "@/lib/ai/generation/normalizeResourceId";

export type ExerciseAiSseDispatchOptions = {
  t: AiGenerationSseTranslate;
  setStreamedText: (s: string) => void;
  setGeneratedExercise: (e: Exercise | null) => void;
  onInvalidateLists: () => void;
  onExerciseGenerated?: (e: Exercise) => void;
};

/**
 * Traite un événement JSON du flux POST generate-ai-stream exercices.
 * Succès + CTA : uniquement si `exercise.id` normalisé est présent (ressource persistée).
 */
export function dispatchExerciseAiSseEvent(
  data: Record<string, unknown>,
  options: ExerciseAiSseDispatchOptions
): void {
  const { t, setStreamedText, setGeneratedExercise, onInvalidateLists, onExerciseGenerated } =
    options;

  if (data.type === "status" && typeof data.message === "string") {
    setStreamedText(data.message);
    return;
  }

  if (data.type === "warning") {
    const raw =
      typeof data.message === "string" && data.message.trim() !== ""
        ? data.message
        : t("aiGenerator.warningFallback");
    toast.warning(t("aiGenerator.warningTitle"), { description: raw });
    return;
  }

  if (data.type === "exercise") {
    const raw = data.exercise as Record<string, unknown> | null | undefined;
    if (!raw || typeof raw !== "object") {
      setStreamedText("");
      toast.error(t("aiGenerator.error"), {
        description: t("aiGenerator.errorDescription"),
      });
      return;
    }
    const title = typeof raw.title === "string" ? raw.title : "";
    if (!title.trim()) {
      setStreamedText("");
      toast.error(t("aiGenerator.error"), {
        description: t("aiGenerator.errorDescription"),
      });
      return;
    }
    const id = normalizeCreatedResourceId(raw.id);
    const topWarning = typeof data.warning === "string" ? data.warning : undefined;
    if (topWarning || id === undefined) {
      setStreamedText("");
      setGeneratedExercise(null);
      toast.warning(t("aiGenerator.warningTitle"), {
        description: topWarning || t("aiGenerator.exerciseNotPersisted"),
      });
      return;
    }
    const exercise = { ...raw, id } as Exercise;
    setGeneratedExercise(exercise);
    setStreamedText("");
    onInvalidateLists();
    toast.success(t("aiGenerator.success"), {
      description: t("aiGenerator.successDescription", { title: exercise.title }),
    });
    onExerciseGenerated?.(exercise);
    return;
  }

  if (data.type === "error") {
    setStreamedText("");
    setGeneratedExercise(null);
    toast.error(t("aiGenerator.error"), {
      description:
        typeof data.message === "string" ? data.message : t("aiGenerator.errorDescription"),
    });
    return;
  }

  if (data.type === "done") {
    setStreamedText("");
  }
}
