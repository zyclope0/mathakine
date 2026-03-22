import { toast } from "sonner";
import type { Challenge } from "@/types/api";
import type { AiGenerationSseTranslate } from "@/lib/ai/generation/types";
import { normalizeCreatedResourceId } from "@/lib/ai/generation/normalizeResourceId";

export type ChallengeAiSseDispatchOptions = {
  t: AiGenerationSseTranslate;
  setStreamedText: (s: string) => void;
  setGeneratedChallenge: (c: Challenge | null) => void;
  onInvalidateLists: () => void;
  onChallengeGenerated?: (c: Challenge) => void;
};

/**
 * Traite un événement JSON du flux POST generate-ai-stream défis.
 * - `warning` (type dédié ou champ sur l'événement `challenge`) : jamais succès navigable.
 * - `challenge` avec `id` normalisé : seul cas qui déclenche la bannière + CTA « Voir le défi ».
 */
export function dispatchChallengeAiSseEvent(
  data: Record<string, unknown>,
  options: ChallengeAiSseDispatchOptions
): void {
  const { t, setStreamedText, setGeneratedChallenge, onInvalidateLists, onChallengeGenerated } =
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

  if (data.type === "challenge") {
    const raw = data.challenge as Record<string, unknown> | null | undefined;
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
    const topWarning = typeof data.warning === "string" ? data.warning : undefined;
    const id = normalizeCreatedResourceId(raw.id);
    if (topWarning || id === undefined) {
      setStreamedText("");
      setGeneratedChallenge(null);
      toast.warning(t("aiGenerator.warningTitle"), {
        description: topWarning || t("aiGenerator.challengeNotPersisted"),
      });
      return;
    }
    const challenge = { ...raw, id } as Challenge;
    setGeneratedChallenge(challenge);
    setStreamedText("");
    onInvalidateLists();
    toast.success(t("aiGenerator.success"), {
      description: t("aiGenerator.successDescription", { title: challenge.title }),
    });
    onChallengeGenerated?.(challenge);
    return;
  }

  if (data.type === "error") {
    setStreamedText("");
    setGeneratedChallenge(null);
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
