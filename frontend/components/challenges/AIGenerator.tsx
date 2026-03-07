"use client";

import { useState, useRef, useEffect } from "react";
import { toast } from "sonner";
import {
  CHALLENGE_TYPES,
  AGE_GROUPS,
  CHALLENGE_PROMPT_SUGGESTIONS,
} from "@/lib/constants/challenges";
import { useChallengeTranslations } from "@/hooks/useChallengeTranslations";
import type { Challenge } from "@/types/api";
import { useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import { useAuth } from "@/hooks/useAuth";
import { ensureFrontendAuthCookie } from "@/lib/api/client";
import { debugLog, debugError } from "@/lib/utils/debug";
import {
  AIGeneratorBase,
  type AIGeneratedItem,
  type AISelectOption,
} from "@/components/shared/AIGeneratorBase";

interface AIGeneratorProps {
  onChallengeGenerated?: (challenge: Challenge) => void;
  /** Mode toolbar compact (comme page Exercices) */
  compact?: boolean;
}

export function AIGenerator({ onChallengeGenerated, compact = false }: AIGeneratorProps) {
  const [isGenerating, setIsGenerating] = useState(false);
  const [streamedText, setStreamedText] = useState("");
  const [generatedChallenge, setGeneratedChallenge] = useState<Challenge | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  const queryClient = useQueryClient();
  const router = useRouter();
  const t = useTranslations("challenges");
  const { getTypeDisplay, getAgeDisplay } = useChallengeTranslations();
  const { user, isLoading: isAuthLoading } = useAuth();

  useEffect(() => {
    return () => {
      abortControllerRef.current?.abort();
    };
  }, []);

  const handleGenerate = async (type: string, ageGroup: string, prompt: string) => {
    if (isGenerating) return;

    if (!user) {
      debugError("[AIGenerator challenges] User not authenticated");
      toast.error(t("aiGenerator.authRequired"), {
        description: t("aiGenerator.authRequiredDescription"),
        action: { label: t("aiGenerator.login"), onClick: () => router.push("/login") },
      });
      return;
    }

    debugLog("[AIGenerator challenges] Starting generation");
    setIsGenerating(true);
    setStreamedText("");
    setGeneratedChallenge(null);

    try {
      const params = new URLSearchParams({ challenge_type: type, age_group: ageGroup });
      if (prompt.trim()) params.append("prompt", prompt.trim());

      const abortController = new AbortController();
      abortControllerRef.current = abortController;

      await ensureFrontendAuthCookie();

      const response = await fetch(`/api/challenges/generate-ai-stream?${params}`, {
        method: "GET",
        headers: { Accept: "text/event-stream" },
        signal: abortController.signal,
      });

      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) throw new Error("No response body");

      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) {
          setIsGenerating(false);
          break;
        }

        const newChunk = decoder.decode(value, { stream: true });
        buffer += newChunk;

        if (newChunk) debugLog("[AIGenerator challenges] chunk:", newChunk.substring(0, 100));

        const lines = buffer.split("\n");
        buffer = lines.pop() || "";

        for (const line of lines) {
          const trimmed = line.trim();
          if (!trimmed.startsWith("data: ")) continue;

          try {
            const data = JSON.parse(trimmed.slice(6));
            debugLog("[AIGenerator challenges] SSE:", data.type);

            if (data.type === "status") {
              setStreamedText(data.message);
            } else if (data.type === "challenge") {
              const challenge = data.challenge as Challenge;
              if (!challenge?.title) {
                debugError("[AIGenerator challenges] Challenge invalide:", challenge);
                toast.error(t("aiGenerator.error"), {
                  description: t("aiGenerator.errorDescription"),
                });
                setStreamedText("");
                setIsGenerating(false);
                return;
              }
              setGeneratedChallenge(challenge);
              setStreamedText("");
              setIsGenerating(false);
              queryClient.invalidateQueries({ queryKey: ["challenges"] });
              queryClient.invalidateQueries({ queryKey: ["completed-challenges"] });
              toast.success(t("aiGenerator.success"), {
                description: t("aiGenerator.successDescription", { title: challenge.title }),
              });
              onChallengeGenerated?.(challenge);
              return;
            } else if (data.type === "error") {
              setStreamedText("");
              setIsGenerating(false);
              toast.error(t("aiGenerator.error"), {
                description: data.message || t("aiGenerator.errorDescription"),
              });
              return;
            } else if (data.type === "done") {
              setStreamedText("");
              setIsGenerating(false);
              return;
            }
          } catch (parseError) {
            debugError(`[AIGenerator challenges] parse error on line "${trimmed}":`, parseError);
          }
        }
      }
    } catch (error) {
      if (error instanceof Error && error.name === "AbortError") {
        debugLog("[AIGenerator challenges] Annulé par l'utilisateur");
        setIsGenerating(false);
        return;
      }
      debugError("[AIGenerator challenges] Erreur génération:", error);
      setIsGenerating(false);
      toast.error(t("aiGenerator.connectionError"), {
        description: t("aiGenerator.connectionErrorDescription"),
      });
    }
  };

  const handleCancel = () => {
    abortControllerRef.current?.abort();
    abortControllerRef.current = null;
    setIsGenerating(false);
    setStreamedText("");
  };

  const handleViewChallenge = () => {
    if (generatedChallenge?.id) router.push(`/challenge/${generatedChallenge.id}`);
  };

  const typeOptions: AISelectOption[] = Object.values(CHALLENGE_TYPES).map((v) => ({
    value: v,
    label: getTypeDisplay(v),
  }));

  const ageOptions: AISelectOption[] = Object.values(AGE_GROUPS).map((v) => ({
    value: v,
    label: getAgeDisplay(v),
  }));

  const generatedItem: AIGeneratedItem | null = generatedChallenge
    ? { id: generatedChallenge.id, title: generatedChallenge.title }
    : null;

  return (
    <AIGeneratorBase
      compact={compact}
      title={t("aiGenerator.title")}
      description={t("aiGenerator.description")}
      typeLabel={t("aiGenerator.challengeType")}
      typeSelectId="ai-challenge-type"
      ageSelectId="ai-challenge-age-group"
      ageLabel={t("aiGenerator.ageGroup")}
      promptLabel={t("aiGenerator.customPrompt")}
      promptPlaceholder={t("aiGenerator.customPromptPlaceholder")}
      generateLabel={t("aiGenerator.generate")}
      generatingLabel={t("aiGenerator.generating")}
      cancelLabel={t("aiGenerator.cancel")}
      viewItemLabel={t("aiGenerator.viewChallenge")}
      successLabel={t("aiGenerator.success")}
      closeAriaLabel={t("aiGenerator.close", { default: "Fermer" })}
      promptSuggestions={[...CHALLENGE_PROMPT_SUGGESTIONS]}
      typeOptions={typeOptions}
      defaultType={CHALLENGE_TYPES.SEQUENCE}
      ageOptions={ageOptions}
      defaultAge={AGE_GROUPS.GROUP_9_11}
      isGenerating={isGenerating}
      streamedText={streamedText}
      generatedItem={generatedItem}
      onGenerate={handleGenerate}
      onCancel={handleCancel}
      onViewItem={handleViewChallenge}
      onDismissResult={() => setGeneratedChallenge(null)}
      isAuthenticated={!!user}
      isAuthLoading={isAuthLoading}
      showAuthBanner={true}
      authBannerTitle={t("aiGenerator.authRequired")}
      authBannerDescription={t("aiGenerator.authRequiredDescription")}
    />
  );
}
