"use client";

import { useState, useRef, useEffect } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import { useAuth } from "@/hooks/useAuth";
import { validateExerciseParams, validateAIPrompt } from "@/lib/validation/exercise";
import { consumeSseJsonEvents } from "@/lib/utils/ssePostStream";
import { toast } from "sonner";
import type { Exercise } from "@/types/api";
import { dispatchExerciseAiSseEvent } from "@/lib/ai/generation/dispatchExerciseAiSseEvent";
import { getAiGenerationRequestErrorToast } from "@/lib/ai/generation/getAiGenerationRequestErrorToast";
import {
  AiGenerationRequestError,
  postAiGenerationSse,
  AI_GENERATION_SSE_PATH,
} from "@/lib/ai/generation/postAiGenerationSse";

interface UseAIExerciseGeneratorOptions {
  onExerciseGenerated?: ((exercise: Exercise) => void) | undefined;
}

/**
 * Hook partagé pour la génération IA d'exercices (POST + flux SSE via fetch).
 * Client SSE : `postAiGenerationSse` ; dispatch événements : `dispatchExerciseAiSseEvent`.
 *
 * Utilisé par : UnifiedExerciseGenerator, AIGenerator (exercises).
 */
export function useAIExerciseGenerator({
  onExerciseGenerated,
}: UseAIExerciseGeneratorOptions = {}) {
  const [isGenerating, setIsGenerating] = useState(false);
  const [streamedText, setStreamedText] = useState("");
  const [generatedExercise, setGeneratedExercise] = useState<Exercise | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  const queryClient = useQueryClient();
  const router = useRouter();
  const t = useTranslations("exercises");
  const { user } = useAuth();

  useEffect(() => {
    return () => {
      abortControllerRef.current?.abort();
    };
  }, []);

  const generate = async (type: string, ageGroup: string, prompt: string) => {
    if (isGenerating) return;

    if (!user) {
      toast.error(t("aiGenerator.authRequired"), {
        description: t("aiGenerator.authRequiredDescription"),
        action: { label: t("aiGenerator.login"), onClick: () => router.push("/login") },
      });
      return;
    }

    const validation = validateExerciseParams({ exercise_type: type, age_group: ageGroup });
    if (!validation.valid) {
      toast.error(t("aiGenerator.validationError"), {
        description: validation.errors.join(", "),
      });
      return;
    }

    if (prompt.trim()) {
      const promptValidation = validateAIPrompt(prompt.trim());
      if (!promptValidation.valid) {
        toast.error(t("aiGenerator.promptValidationError"), {
          description: promptValidation.errors.join(", "),
        });
        return;
      }
    }

    setIsGenerating(true);
    setStreamedText("");
    setGeneratedExercise(null);

    const abortController = new AbortController();
    abortControllerRef.current = abortController;

    try {
      const response = await postAiGenerationSse(
        AI_GENERATION_SSE_PATH.exercise,
        {
          exercise_type: type,
          age_group: ageGroup,
          prompt: prompt.trim(),
        },
        abortController.signal
      );

      if (!response.ok) {
        let description = t("aiGenerator.errorDescription");
        try {
          const errBody = (await response.json()) as { error?: string; detail?: unknown };
          if (typeof errBody.error === "string") description = errBody.error;
        } catch {
          /* ignore */
        }
        toast.error(t("aiGenerator.error"), { description });
        return;
      }

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
          dispatchExerciseAiSseEvent(data as Record<string, unknown>, {
            t,
            setStreamedText,
            setGeneratedExercise,
            onInvalidateLists: () => {
              setTimeout(() => {
                queryClient.invalidateQueries({ queryKey: ["exercises"] });
              }, 100);
            },
            ...(onExerciseGenerated !== undefined ? { onExerciseGenerated } : {}),
          });
        },
        { signal: abortController.signal }
      );
    } catch (e) {
      if (e instanceof DOMException && e.name === "AbortError") {
        return;
      }
      if (e instanceof AiGenerationRequestError) {
        setStreamedText("");
        const { title, description } = getAiGenerationRequestErrorToast(e, t);
        toast.error(title, {
          description,
          ...(e.code === "http_401" || e.code === "csrf_token_missing"
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
      setStreamedText("");
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
    generatedExercise,
    setGeneratedExercise,
    generate,
    cancel,
  };
}
