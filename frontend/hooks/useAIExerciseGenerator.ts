"use client";

import { useState, useRef, useEffect } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import { useAuth } from "@/hooks/useAuth";
import { ensureFrontendAuthCookie } from "@/lib/api/client";
import { validateExerciseParams, validateAIPrompt } from "@/lib/validation/exercise";
import { toast } from "sonner";
import type { Exercise } from "@/types/api";

interface UseAIExerciseGeneratorOptions {
  onExerciseGenerated?: ((exercise: Exercise) => void) | undefined;
}

/**
 * Hook partagé pour la génération IA d'exercices via EventSource.
 * Encapsule l'état (isGenerating, streamedText, generatedExercise) et
 * les callbacks (generate, cancel).
 *
 * Utilisé par : UnifiedExerciseGenerator, AIGenerator (exercises).
 */
export function useAIExerciseGenerator({
  onExerciseGenerated,
}: UseAIExerciseGeneratorOptions = {}) {
  const [isGenerating, setIsGenerating] = useState(false);
  const [streamedText, setStreamedText] = useState("");
  const [generatedExercise, setGeneratedExercise] = useState<Exercise | null>(null);
  const eventSourceRef = useRef<EventSource | null>(null);

  const queryClient = useQueryClient();
  const router = useRouter();
  const t = useTranslations("exercises");
  const { user } = useAuth();

  useEffect(() => {
    return () => {
      eventSourceRef.current?.close();
    };
  }, []);

  const generate = (type: string, ageGroup: string, prompt: string) => {
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

    ensureFrontendAuthCookie()
      .then(() => {
        const params = new URLSearchParams({ exercise_type: type, age_group: ageGroup });
        if (prompt.trim()) params.append("prompt", prompt.trim());

        const eventSource = new EventSource(`/api/exercises/generate-ai-stream?${params}`);
        eventSourceRef.current = eventSource;

        eventSource.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            if (data.type === "status") {
              setStreamedText(data.message);
            } else if (data.type === "exercise") {
              const exercise = data.exercise as Exercise;
              setGeneratedExercise(exercise);
              setStreamedText("");
              eventSource.close();
              eventSourceRef.current = null;
              setIsGenerating(false);
              setTimeout(() => {
                queryClient.invalidateQueries({ queryKey: ["exercises"] });
              }, 100);
              toast.success(t("aiGenerator.success"), {
                description: t("aiGenerator.successDescription", { title: exercise.title }),
              });
              onExerciseGenerated?.(exercise);
            } else if (data.type === "error") {
              setStreamedText("");
              eventSource.close();
              eventSourceRef.current = null;
              setIsGenerating(false);
              toast.error(t("aiGenerator.error"), {
                description: data.message || t("aiGenerator.errorDescription"),
              });
            }
          } catch {
            // Parsing SSE silencieux
          }
        };

        eventSource.onerror = () => {
          setStreamedText("");
          eventSource.close();
          eventSourceRef.current = null;
          setIsGenerating(false);
          toast.error(t("aiGenerator.connectionError"), {
            description: t("aiGenerator.connectionErrorDescription"),
          });
        };
      })
      .catch(() => {
        setIsGenerating(false);
        toast.error(t("aiGenerator.startError"), {
          description: t("aiGenerator.startErrorDescription"),
        });
      });
  };

  const cancel = () => {
    eventSourceRef.current?.close();
    eventSourceRef.current = null;
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
