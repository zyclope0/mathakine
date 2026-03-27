"use client";

import { useState, useRef, useEffect } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import { useAuth } from "@/hooks/useAuth";
import { toast } from "sonner";
import type { Challenge } from "@/types/api";
import { dispatchChallengeAiSseEvent } from "@/lib/ai/generation/dispatchChallengeAiSseEvent";
import { consumeSseJsonEvents } from "@/lib/utils/ssePostStream";
import { getAiGenerationRequestErrorToast } from "@/lib/ai/generation/getAiGenerationRequestErrorToast";
import {
  AiGenerationRequestError,
  postAiGenerationSse,
  AI_GENERATION_SSE_PATH,
} from "@/lib/ai/generation/postAiGenerationSse";
import { debugLog, debugError } from "@/lib/utils/debug";
import { CHALLENGE_AI_AGE_USE_PROFILE } from "@/lib/constants/challenges";

interface UseAIChallengeGeneratorOptions {
  onChallengeGenerated?: ((challenge: Challenge) => void) | undefined;
}

/**
 * Hook partagé pour la génération IA des défis (POST + SSE).
 * Miroir de useAIExerciseGenerator : état, annulation, dispatch centralisé.
 */
export function useAIChallengeGenerator({
  onChallengeGenerated,
}: UseAIChallengeGeneratorOptions = {}) {
  const [isGenerating, setIsGenerating] = useState(false);
  const [streamedText, setStreamedText] = useState("");
  const [generatedChallenge, setGeneratedChallenge] = useState<Challenge | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  const queryClient = useQueryClient();
  const router = useRouter();
  const t = useTranslations("challenges");
  const { user } = useAuth();

  useEffect(() => {
    return () => {
      abortControllerRef.current?.abort();
    };
  }, []);

  const generate = async (type: string, ageGroup: string, prompt: string) => {
    if (isGenerating) return;

    if (!user) {
      debugError("[useAIChallengeGenerator] User not authenticated");
      toast.error(t("aiGenerator.authRequired"), {
        description: t("aiGenerator.authRequiredDescription"),
        action: { label: t("aiGenerator.login"), onClick: () => router.push("/login") },
      });
      return;
    }

    debugLog("[useAIChallengeGenerator] Starting generation");
    setIsGenerating(true);
    setStreamedText("");
    setGeneratedChallenge(null);

    const abortController = new AbortController();
    abortControllerRef.current = abortController;

    try {
      const body: Record<string, unknown> = {
        challenge_type: type,
        prompt: prompt.trim(),
      };
      if (ageGroup !== CHALLENGE_AI_AGE_USE_PROFILE) {
        body.age_group = ageGroup;
      }

      const response = await postAiGenerationSse(
        AI_GENERATION_SSE_PATH.challenge,
        body,
        abortController.signal
      );

      const contentType = response.headers.get("content-type") ?? "";
      if (!contentType.includes("text/event-stream")) {
        toast.error(t("aiGenerator.connectionError"), {
          description: t("aiGenerator.connectionErrorDescription"),
        });
        return;
      }

      await consumeSseJsonEvents(
        response,
        (data) => {
          debugLog("[useAIChallengeGenerator] SSE:", data.type);
          dispatchChallengeAiSseEvent(data as Record<string, unknown>, {
            t,
            setStreamedText,
            setGeneratedChallenge,
            onInvalidateLists: () => {
              queryClient.invalidateQueries({ queryKey: ["challenges"] });
              queryClient.invalidateQueries({ queryKey: ["completed-challenges"] });
            },
            ...(onChallengeGenerated !== undefined ? { onChallengeGenerated } : {}),
          });
        },
        { signal: abortController.signal }
      );
    } catch (error) {
      const isAbort =
        (error instanceof Error && error.name === "AbortError") ||
        (error instanceof DOMException && error.name === "AbortError");
      if (isAbort) {
        debugLog("[useAIChallengeGenerator] Annulé par l'utilisateur");
        return;
      }
      if (error instanceof AiGenerationRequestError) {
        setStreamedText("");
        const { title, description } = getAiGenerationRequestErrorToast(error, t);
        toast.error(title, {
          description,
          ...(error.code === "http_401" || error.code === "csrf_token_missing"
            ? {
                action: {
                  label: t("aiGenerator.login"),
                  onClick: () => router.push("/login"),
                },
              }
            : {}),
        });
        return;
      }
      debugError("[useAIChallengeGenerator] Erreur génération:", error);
      toast.error(t("aiGenerator.connectionError"), {
        description: t("aiGenerator.connectionErrorDescription"),
      });
    } finally {
      abortControllerRef.current = null;
      setIsGenerating(false);
    }
  };

  const cancel = () => {
    abortControllerRef.current?.abort();
    abortControllerRef.current = null;
    setIsGenerating(false);
    setStreamedText("");
  };

  return {
    isGenerating,
    streamedText,
    generatedChallenge,
    setGeneratedChallenge,
    generate,
    cancel,
  };
}
