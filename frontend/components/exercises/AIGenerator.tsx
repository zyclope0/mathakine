"use client";

import { EXERCISE_TYPES, AGE_GROUPS, EXERCISE_PROMPT_SUGGESTIONS } from "@/lib/constants/exercises";
import { useExerciseTranslations } from "@/hooks/useChallengeTranslations";
import type { Exercise } from "@/types/api";
import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import { useAuth } from "@/hooks/useAuth";
import { useAIExerciseGenerator } from "@/hooks/useAIExerciseGenerator";
import { normalizeCreatedResourceId } from "@/lib/ai/generation/normalizeResourceId";
import {
  AIGeneratorBase,
  type AIGeneratedItem,
  type AISelectOption,
} from "@/components/shared/AIGeneratorBase";

interface AIGeneratorProps {
  onExerciseGenerated?: (exercise: Exercise) => void;
}

export function AIGenerator({ onExerciseGenerated }: AIGeneratorProps) {
  const router = useRouter();
  const t = useTranslations("exercises");
  const { getTypeDisplay, getAgeDisplay } = useExerciseTranslations();
  const { user } = useAuth();

  const { isGenerating, streamedText, generatedExercise, setGeneratedExercise, generate, cancel } =
    useAIExerciseGenerator({ onExerciseGenerated });

  const typeOptions: AISelectOption[] = Object.values(EXERCISE_TYPES).map((v) => ({
    value: v,
    label: getTypeDisplay(v),
  }));

  const ageOptions: AISelectOption[] = Object.values(AGE_GROUPS).map((v) => ({
    value: v,
    label: getAgeDisplay(v),
  }));

  const persistedId = generatedExercise
    ? normalizeCreatedResourceId(generatedExercise.id)
    : undefined;
  const generatedItem: AIGeneratedItem | null = generatedExercise
    ? {
        ...(persistedId !== undefined ? { id: persistedId } : {}),
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
      ageSelectId="ai-exercise-age-group"
      ageLabel={t("aiGenerator.ageGroup")}
      promptLabel={t("aiGenerator.customPrompt")}
      promptPlaceholder={t("aiGenerator.customPromptPlaceholder")}
      generateLabel={t("aiGenerator.generate")}
      generatingLabel={t("aiGenerator.generating")}
      cancelLabel={t("aiGenerator.cancel")}
      viewItemLabel={t("aiGenerator.viewExercise")}
      successLabel={t("aiGenerator.exerciseGenerated")}
      closeAriaLabel={t("aiGenerator.close", { default: "Fermer" })}
      promptSuggestions={[...EXERCISE_PROMPT_SUGGESTIONS]}
      typeOptions={typeOptions}
      defaultType={EXERCISE_TYPES.ADDITION}
      ageOptions={ageOptions}
      defaultAge={AGE_GROUPS.GROUP_6_8}
      isGenerating={isGenerating}
      streamedText={streamedText}
      generatedItem={generatedItem}
      onGenerate={generate}
      onCancel={cancel}
      onViewItem={() => {
        const id = generatedExercise ? normalizeCreatedResourceId(generatedExercise.id) : undefined;
        if (id) router.push(`/exercises/${id}`);
      }}
      onDismissResult={() => setGeneratedExercise(null)}
      isAuthenticated={!!user}
      showAuthBanner={false}
    />
  );
}
