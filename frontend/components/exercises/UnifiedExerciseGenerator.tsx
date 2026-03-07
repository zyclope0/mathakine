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
import { Loader2, Zap, Sparkles, X, HelpCircle } from "lucide-react";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { toast } from "sonner";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { cn } from "@/lib/utils";
import type { Exercise } from "@/types/api";

const PROMPT_SUGGESTIONS = EXERCISE_PROMPT_SUGGESTIONS;

interface UnifiedExerciseGeneratorProps {
  onExerciseGenerated?: (exercise: Exercise) => void;
}

export function UnifiedExerciseGenerator({ onExerciseGenerated }: UnifiedExerciseGeneratorProps) {
  const t = useTranslations("exercises");
  const { getTypeDisplay, getAgeDisplay } = useExerciseTranslations();
  const { generateExercise, isGenerating: isQuickGenerating } = useExercises();
  const router = useRouter();

  const [exerciseType, setExerciseType] = useState<string>(EXERCISE_TYPES.ADDITION);
  const [ageGroup, setAgeGroup] = useState<string>(AGE_GROUPS.GROUP_6_8);
  const [isIAEnabled, setIsIAEnabled] = useState(false);
  const [customPrompt, setCustomPrompt] = useState("");

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

  const handleQuickGenerate = () => {
    const validation = validateExerciseParams({ exercise_type: exerciseType, age_group: ageGroup });
    if (!validation.valid) {
      toast.error("Erreur de validation", { description: validation.errors.join(", ") });
      return;
    }
    generateExercise({ exercise_type: exerciseType, age_group: ageGroup, save: true });
  };

  const handleGenerate = () => {
    if (isIAEnabled) {
      generateAI(exerciseType, ageGroup, customPrompt);
    } else {
      handleQuickGenerate();
    }
  };

  return (
    <div className="rounded-xl border border-border/50 bg-card/40 backdrop-blur-md p-4 animate-fade-in-up-delay-1">
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
              Mode IA ✨
            </label>
            <TooltipProvider delayDuration={200}>
              <Tooltip>
                <TooltipTrigger asChild>
                  <HelpCircle
                    className="h-3.5 w-3.5 text-muted-foreground hover:text-primary cursor-help"
                    aria-label="En savoir plus sur le Mode IA"
                  />
                </TooltipTrigger>
                <TooltipContent
                  side="top"
                  className="max-w-[230px] bg-card border border-border/50 p-3 rounded-lg"
                >
                  <p className="text-xs leading-relaxed text-foreground">
                    ✨ L&apos;IA génère un exercice unique basé sur un scénario créatif de ton
                    choix. Plus lent que le mode classique, mais bien plus imaginatif !
                  </p>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
            <Switch
              id="ia-mode-switch"
              checked={isIAEnabled}
              onCheckedChange={(val) => {
                setIsIAEnabled(val);
                if (!val) setCustomPrompt("");
              }}
              aria-label="Activer le mode génération IA"
            />
          </div>
          <Button
            onClick={handleGenerate}
            disabled={isGenerating}
            size="sm"
            className={cn(
              "h-9 transition-all",
              isIAEnabled &&
                "shadow-[0_0_12px_color-mix(in_srgb,var(--primary)_20%,transparent)]"
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
                <label htmlFor="unified-ai-prompt" className="text-xs text-muted-foreground mb-1 block">
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
                <div className="p-2.5 rounded-lg bg-card/60 border border-border/50 flex items-center gap-2">
                  <Loader2 className="h-4 w-4 animate-spin text-primary flex-shrink-0" />
                  <p className="flex-1 text-xs text-muted-foreground truncate">
                    {streamedText || t("aiGenerator.generating")}
                  </p>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={cancelAI}
                    className="h-6 w-6 p-0 flex-shrink-0"
                    aria-label={t("aiGenerator.cancel")}
                  >
                    <X className="h-3 w-3" />
                  </Button>
                </div>
              )}

              {generatedExercise && !isAIGenerating && (
                <div className="p-2.5 rounded-lg bg-success/10 border border-success/20 flex items-center justify-between gap-3">
                  <div className="flex-1 min-w-0">
                    <p className="text-xs font-medium text-success mb-0.5">
                      {t("aiGenerator.exerciseGenerated")}
                    </p>
                    <p className="text-sm text-foreground truncate">{generatedExercise.title}</p>
                  </div>
                  <div className="flex items-center gap-2 flex-shrink-0">
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => router.push(`/exercises/${generatedExercise.id}`)}
                      className="h-7 text-xs"
                    >
                      {t("aiGenerator.viewExercise")}
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => setGeneratedExercise(null)}
                      className="h-7 w-7 p-0"
                      aria-label={t("aiGenerator.close")}
                    >
                      <X className="h-3.5 w-3.5" />
                    </Button>
                  </div>
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
