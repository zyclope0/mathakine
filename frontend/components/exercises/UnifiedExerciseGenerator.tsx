"use client";

import { useState } from "react";
import { useExercises } from "@/hooks/useExercises";
import { useTranslations } from "next-intl";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { EXERCISE_TYPES, AGE_GROUPS, EXERCISE_PROMPT_SUGGESTIONS } from "@/lib/constants/exercises";
import { useExerciseTranslations } from "@/hooks/useChallengeTranslations";
import { useAIExerciseGenerator } from "@/hooks/useAIExerciseGenerator";
import { validateExerciseParams } from "@/lib/validation/exercise";
import { Loader2, Zap, Sparkles, HelpCircle } from "lucide-react";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { toast } from "sonner";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { cn } from "@/lib/utils";
import type { Exercise } from "@/types/api";
import { normalizeCreatedResourceId } from "@/lib/ai/generation/normalizeResourceId";
import {
  AIGeneratorStreamingRow,
  AIGeneratorSuccessRowCompact,
} from "@/components/shared/aiGeneratorSharedUi";

const PROMPT_SUGGESTIONS = EXERCISE_PROMPT_SUGGESTIONS;

interface UnifiedExerciseGeneratorProps {
  onExerciseGenerated?: (exercise: Exercise) => void;
}

export function UnifiedExerciseGenerator({ onExerciseGenerated }: UnifiedExerciseGeneratorProps) {
  const t = useTranslations("exercises");
  const { getTypeDisplay, getAgeDisplay } = useExerciseTranslations();
  const { generateExerciseAsync, isGenerating: isQuickGenerating } = useExercises();
  const router = useRouter();

  const [exerciseType, setExerciseType] = useState<string>(EXERCISE_TYPES.ADDITION);
  const [ageGroup, setAgeGroup] = useState<string>(AGE_GROUPS.GROUP_6_8);
  const [isIAEnabled, setIsIAEnabled] = useState(false);
  const [customPrompt, setCustomPrompt] = useState("");
  /** Exercice créé par la génération rapide (hors IA) — pour CTA « Voir l'exercice ». */
  const [quickGeneratedExercise, setQuickGeneratedExercise] = useState<Exercise | null>(null);

  // Logique IA déléguée au hook partagé
  const {
    isGenerating: isAIGenerating,
    streamedText,
    generatedExercise,
    setGeneratedExercise,
    generate: generateAI,
    cancel: cancelAI,
  } = useAIExerciseGenerator({ onExerciseGenerated });

  const isGenerating = isIAEnabled ? isAIGenerating : isQuickGenerating;

  const handleQuickGenerate = async () => {
    const validation = validateExerciseParams({ exercise_type: exerciseType, age_group: ageGroup });
    if (!validation.valid) {
      toast.error("Erreur de validation", { description: validation.errors.join(", ") });
      return;
    }
    setQuickGeneratedExercise(null);
    try {
      const created = await generateExerciseAsync({
        exercise_type: exerciseType,
        age_group: ageGroup,
        save: true,
      });
      setQuickGeneratedExercise(created);
      onExerciseGenerated?.(created);
    } catch {
      /* erreur déjà toastée par useExercises (onError) */
    }
  };

  const handleGenerate = () => {
    if (isIAEnabled) {
      generateAI(exerciseType, ageGroup, customPrompt);
    } else {
      handleQuickGenerate();
    }
  };

  return (
    <div className="rounded-xl border border-border/50 bg-card p-4 animate-fade-in-up-delay-1">
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
        {/* Bloc Titre (gauche) */}
        <div className="flex items-center gap-2 flex-shrink-0">
          <div className="flex items-center justify-center p-1.5 rounded-lg bg-primary/10">
            <Zap className="h-4 w-4 text-primary" aria-hidden="true" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-foreground">{t("generator.title")}</h3>
            <p className="text-xs text-muted-foreground hidden lg:block">
              {t("generator.description")}
            </p>
          </div>
        </div>

        {/* Bloc Contrôles (centre) */}
        <div className="flex flex-wrap items-center gap-3">
          <Select value={exerciseType} onValueChange={setExerciseType} disabled={isGenerating}>
            <SelectTrigger id="unified-exercise-type" className="h-9 w-[130px]">
              <SelectValue placeholder={t("generator.selectType")} />
            </SelectTrigger>
            <SelectContent>
              {Object.values(EXERCISE_TYPES).map((type) => (
                <SelectItem key={type} value={type}>
                  {getTypeDisplay(type)}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Select value={ageGroup} onValueChange={setAgeGroup} disabled={isGenerating}>
            <SelectTrigger id="unified-age-group" className="h-9 w-[110px]">
              <SelectValue placeholder={t("generator.selectAgeGroup")} />
            </SelectTrigger>
            <SelectContent>
              {Object.values(AGE_GROUPS).map((group) => (
                <SelectItem key={group} value={group}>
                  {getAgeDisplay(group)}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Bloc Actions (droite) */}
        <div className="flex items-center gap-4 flex-shrink-0">
          <div className="flex items-center gap-2">
            <label
              htmlFor="ia-mode-switch"
              className={cn(
                "text-xs font-medium cursor-pointer select-none",
                isIAEnabled ? "text-primary" : "text-muted-foreground"
              )}
            >
              {t("generator.iaModeLabel")}
            </label>
            <TooltipProvider delayDuration={200}>
              <Tooltip>
                <TooltipTrigger asChild>
                  <HelpCircle
                    className="h-3.5 w-3.5 text-muted-foreground hover:text-primary cursor-help"
                    aria-label={t("generator.iaModeHelpAriaLabel")}
                  />
                </TooltipTrigger>
                <TooltipContent
                  side="top"
                  className="max-w-[230px] bg-card border border-border/50 p-3 rounded-lg"
                >
                  <p className="text-xs leading-relaxed text-foreground">
                    {t("generator.iaModeHelpText")}
                  </p>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
            <Switch
              id="ia-mode-switch"
              checked={isIAEnabled}
              onCheckedChange={(val) => {
                setIsIAEnabled(val);
                if (val) {
                  setQuickGeneratedExercise(null);
                } else {
                  setCustomPrompt("");
                  setGeneratedExercise(null);
                }
              }}
              aria-label={t("generator.iaModeAriaLabel")}
            />
          </div>
          <Button
            onClick={handleGenerate}
            disabled={isGenerating}
            size="sm"
            className={cn(
              "h-9 transition-all",
              isIAEnabled && "shadow-[0_0_12px_color-mix(in_srgb,var(--primary)_20%,transparent)]"
            )}
          >
            {isGenerating ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" aria-hidden="true" />
                {isIAEnabled ? t("aiGenerator.generating") : t("generator.generating")}
              </>
            ) : isIAEnabled ? (
              <>
                <Sparkles className="mr-2 h-4 w-4" aria-hidden="true" />
                {t("aiGenerator.generate")}
              </>
            ) : (
              <>
                <Zap className="mr-2 h-4 w-4" aria-hidden="true" />
                {t("generator.generate")}
              </>
            )}
          </Button>
        </div>
      </div>

      {!isIAEnabled && quickGeneratedExercise && !isQuickGenerating && (
        <AIGeneratorSuccessRowCompact
          successLabel={t("aiGenerator.exerciseGenerated")}
          title={quickGeneratedExercise.title}
          viewItemLabel={t("aiGenerator.viewExercise")}
          onViewItem={() => {
            const id = normalizeCreatedResourceId(quickGeneratedExercise.id);
            if (id) router.push(`/exercises/${id}`);
          }}
          showViewButton={normalizeCreatedResourceId(quickGeneratedExercise.id) !== undefined}
          onDismiss={() => setQuickGeneratedExercise(null)}
          closeAriaLabel={t("aiGenerator.close")}
          rootClassName="mt-4 p-2.5"
        />
      )}

      {/* Zone IA — affichage conditionnel (mobile + desktop quand activé) */}
      <AnimatePresence initial={false}>
        {isIAEnabled && (
          <motion.div
            key="ia-zone"
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3, ease: [0.4, 0, 0.2, 1] }}
            className="overflow-hidden mt-4"
          >
            <div className="space-y-3 pt-2 border-t border-border/50">
              <div>
                <label
                  htmlFor="unified-ai-prompt"
                  className="text-xs text-muted-foreground mb-1 block"
                >
                  {t("aiGenerator.customPrompt")}
                </label>
                <Textarea
                  id="unified-ai-prompt"
                  value={customPrompt}
                  onChange={(e) => setCustomPrompt(e.target.value)}
                  placeholder="Ex: Une mission de sauvetage sur Mars avec des fractions..."
                  className="resize-none min-h-[70px] border-border/50 bg-background/60 text-sm"
                  disabled={isGenerating}
                  rows={2}
                />
              </div>
              <div className="flex flex-wrap gap-1.5">
                {PROMPT_SUGGESTIONS.map((suggestion) => (
                  <button
                    key={suggestion}
                    type="button"
                    onClick={() => setCustomPrompt(suggestion)}
                    disabled={isGenerating}
                    className="text-xs bg-muted/50 hover:bg-muted text-muted-foreground px-2.5 py-1 rounded-full transition-colors disabled:opacity-40"
                  >
                    {suggestion}
                  </button>
                ))}
              </div>

              {isAIGenerating && (
                <AIGeneratorStreamingRow
                  streamedText={streamedText}
                  fallbackLabel={t("aiGenerator.generating")}
                  cancelLabel={t("aiGenerator.cancel")}
                  onCancel={cancelAI}
                  rootClassName="p-2.5"
                  streamParagraphClassName="truncate"
                  cancelButtonClassName="flex-shrink-0"
                />
              )}

              {generatedExercise && !isAIGenerating && (
                <AIGeneratorSuccessRowCompact
                  successLabel={t("aiGenerator.exerciseGenerated")}
                  title={generatedExercise.title}
                  viewItemLabel={t("aiGenerator.viewExercise")}
                  onViewItem={() => {
                    const id = normalizeCreatedResourceId(generatedExercise.id);
                    if (id) router.push(`/exercises/${id}`);
                  }}
                  showViewButton={normalizeCreatedResourceId(generatedExercise.id) !== undefined}
                  onDismiss={() => setGeneratedExercise(null)}
                  closeAriaLabel={t("aiGenerator.close")}
                  rootClassName="p-2.5"
                />
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
