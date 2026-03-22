"use client";

import {
  CHALLENGE_TYPES,
  AGE_GROUPS,
  CHALLENGE_PROMPT_SUGGESTIONS,
} from "@/lib/constants/challenges";
import { useChallengeTranslations } from "@/hooks/useChallengeTranslations";
import type { Challenge } from "@/types/api";
import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import { useAuth } from "@/hooks/useAuth";
import { useAIChallengeGenerator } from "@/hooks/useAIChallengeGenerator";
import { normalizeCreatedResourceId } from "@/lib/ai/generation/normalizeResourceId";
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
  const router = useRouter();
  const t = useTranslations("challenges");
  const { getTypeDisplay, getAgeDisplay } = useChallengeTranslations();
  const { user, isLoading: isAuthLoading } = useAuth();

  const {
    isGenerating,
    streamedText,
    generatedChallenge,
    setGeneratedChallenge,
    generate,
    cancel,
  } = useAIChallengeGenerator({ onChallengeGenerated });

  const handleViewChallenge = () => {
    const id = generatedChallenge ? normalizeCreatedResourceId(generatedChallenge.id) : undefined;
    if (id) router.push(`/challenge/${id}`);
  };

  const typeOptions: AISelectOption[] = Object.values(CHALLENGE_TYPES).map((v) => ({
    value: v,
    label: getTypeDisplay(v),
  }));

  const ageOptions: AISelectOption[] = Object.values(AGE_GROUPS).map((v) => ({
    value: v,
    label: getAgeDisplay(v),
  }));

  const persistedId = generatedChallenge
    ? normalizeCreatedResourceId(generatedChallenge.id)
    : undefined;
  const generatedItem: AIGeneratedItem | null = generatedChallenge
    ? {
        ...(persistedId !== undefined ? { id: persistedId } : {}),
        title: generatedChallenge.title,
      }
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
      onGenerate={generate}
      onCancel={cancel}
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
