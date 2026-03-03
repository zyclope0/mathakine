"use client";

import { useState, useRef, useEffect } from "react";
import { toast } from "sonner";
import {
  EXERCISE_TYPES,
  AGE_GROUPS,
  type ExerciseType,
  type AgeGroup,
} from "@/lib/constants/exercises";
import { useExerciseTranslations } from "@/hooks/useChallengeTranslations";
import type { Exercise } from "@/types/api";
import { useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import { useAuth } from "@/hooks/useAuth";
import { ensureFrontendAuthCookie } from "@/lib/api/client";
import { validateExerciseParams, validateAIPrompt } from "@/lib/validation/exercise";
import {
  AIGeneratorBase,
  type AIGeneratedItem,
  type AISelectOption,
} from "@/components/shared/AIGeneratorBase";

interface AIGeneratorProps {
  onExerciseGenerated?: (exercise: Exercise) => void;
}

export function AIGenerator({ onExerciseGenerated }: AIGeneratorProps) {
  const [isGenerating, setIsGenerating] = useState(false);
  const [streamedText, setStreamedText] = useState("");
  const [generatedExercise, setGeneratedExercise] = useState<Exercise | null>(null);
  const eventSourceRef = useRef<EventSource | null>(null);

  const queryClient = useQueryClient();
  const router = useRouter();
  const t = useTranslations("exercises");
  const { getTypeDisplay, getAgeDisplay } = useExerciseTranslations();
  const { user } = useAuth();

  useEffect(() => {
    return () => {
      eventSourceRef.current?.close();
    };
  }, []);

  const handleGenerate = (type: string, ageGroup: string, prompt: string) => {
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
            // Erreur de parsing SSE silencieuse
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

  const handleCancel = () => {
    eventSourceRef.current?.close();
    eventSourceRef.current = null;
    setIsGenerating(false);
    setStreamedText("");
  };

  const handleViewExercise = () => {
    if (generatedExercise?.id) router.push(`/exercises/${generatedExercise.id}`);
  };

  const typeOptions: AISelectOption[] = Object.values(EXERCISE_TYPES).map((v) => ({
    value: v,
    label: getTypeDisplay(v),
  }));

  const ageOptions: AISelectOption[] = Object.values(AGE_GROUPS).map((v) => ({
    value: v,
    label: getAgeDisplay(v),
  }));

  const generatedItem: AIGeneratedItem | null = generatedExercise
    ? {
        id: generatedExercise.id,
        title: generatedExercise.title,
        subtitle: generatedExercise.question,
      }
    : null;

  return (
    <AIGeneratorBase
      title={t("aiGenerator.title")}
      description={t("aiGenerator.description")}
      typeLabel={t("aiGenerator.exerciseType")}
      typeSelectId="ai-exercise-type"
      ageLabel={t("aiGenerator.ageGroup")}
      promptLabel={t("aiGenerator.customPrompt")}
      promptPlaceholder={t("aiGenerator.customPromptPlaceholder")}
      generateLabel={t("aiGenerator.generate")}
      generatingLabel={t("aiGenerator.generating")}
      cancelLabel={t("aiGenerator.cancel")}
      viewItemLabel={t("aiGenerator.viewExercise")}
      successLabel={t("aiGenerator.exerciseGenerated")}
      closeAriaLabel={t("aiGenerator.close")}
      typeOptions={typeOptions}
      defaultType={EXERCISE_TYPES.ADDITION}
      ageOptions={ageOptions}
      defaultAge={AGE_GROUPS.GROUP_6_8}
      isGenerating={isGenerating}
      streamedText={streamedText}
      generatedItem={generatedItem}
      onGenerate={handleGenerate}
      onCancel={handleCancel}
      onViewItem={handleViewExercise}
      onDismissResult={() => setGeneratedExercise(null)}
      isAuthenticated={!!user}
      showAuthBanner={false}
    />
  );
}
