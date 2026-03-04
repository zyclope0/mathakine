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
import { Card, CardContent, CardHeader } from "@/components/ui/card";
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
    <Card className="border-white/10 bg-white/5 backdrop-blur-md shadow-lg">
      {/* En-tête avec Switch Mode IA */}
      <CardHeader className="pb-4">
        <div className="flex items-center justify-between gap-4 flex-wrap">
          <div className="flex items-center gap-3">
            <div className="flex items-center justify-center p-2 rounded-lg bg-primary/10 flex-shrink-0">
              <Zap className="h-5 w-5 text-primary" aria-hidden="true" />
            </div>
            <div>
              <h3 className="text-base md:text-lg font-semibold text-foreground">
                {t("generator.title")}
              </h3>
              <p className="text-sm text-muted-foreground hidden sm:block">
                {t("generator.description")}
              </p>
            </div>
          </div>

          {/* Toggle Mode IA */}
          <div className="flex items-center gap-2.5 flex-shrink-0">
            <label
              htmlFor="ia-mode-switch"
              className={cn(
                "text-sm font-medium cursor-pointer transition-colors select-none",
                isIAEnabled ? "text-primary" : "text-muted-foreground"
              )}
            >
              Mode IA ✨
            </label>

            {/* Tooltip explicatif */}
            <TooltipProvider delayDuration={200}>
              <Tooltip>
                <TooltipTrigger asChild>
                  <HelpCircle
                    className="w-4 h-4 text-muted-foreground hover:text-primary transition-colors cursor-help"
                    aria-label="En savoir plus sur le Mode IA"
                  />
                </TooltipTrigger>
                <TooltipContent
                  side="top"
                  className="max-w-[230px] bg-slate-900/90 backdrop-blur-md border border-white/10 text-slate-200 p-3 rounded-lg shadow-xl"
                >
                  <p className="text-xs leading-relaxed">
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
        </div>
      </CardHeader>

      <CardContent className="space-y-5">
        <div className="max-w-4xl mx-auto space-y-5">
          {/* Sélecteurs toujours visibles */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-2">
              <label htmlFor="unified-exercise-type" className="text-sm font-medium">
                {t("generator.exerciseType")}
              </label>
              <Select value={exerciseType} onValueChange={setExerciseType} disabled={isGenerating}>
                <SelectTrigger id="unified-exercise-type">
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
            </div>

            <div className="space-y-2">
              <label htmlFor="unified-age-group" className="text-sm font-medium">
                {t("generator.ageGroup")}
              </label>
              <Select value={ageGroup} onValueChange={setAgeGroup} disabled={isGenerating}>
                <SelectTrigger id="unified-age-group">
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
          </div>

          {/* Zone IA — affichage conditionnel avec animation de hauteur */}
          <AnimatePresence initial={false}>
            {isIAEnabled && (
              <motion.div
                key="ia-zone"
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: "auto", opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                transition={{ duration: 0.3, ease: [0.4, 0, 0.2, 1] }}
                className="overflow-hidden"
              >
                <div className="pt-1 space-y-3">
                  <div className="space-y-1.5">
                    <label htmlFor="unified-ai-prompt" className="text-sm font-medium">
                      {t("aiGenerator.customPrompt")}
                    </label>
                    <Textarea
                      id="unified-ai-prompt"
                      value={customPrompt}
                      onChange={(e) => setCustomPrompt(e.target.value)}
                      placeholder="Ex: Une mission de sauvetage sur Mars avec des fractions..."
                      className="resize-none min-h-[80px] border-primary/30 bg-background/60 transition-all focus-visible:ring-2 focus-visible:ring-primary/50 focus-visible:border-primary"
                      disabled={isGenerating}
                      rows={3}
                    />

                    {/* Badges d'inspiration */}
                    <div className="pt-1">
                      <p className="text-xs text-muted-foreground/70 mb-2">
                        Manque d&apos;inspiration ?
                      </p>
                      <div className="flex flex-wrap gap-1.5">
                        {PROMPT_SUGGESTIONS.map((suggestion) => (
                          <button
                            key={suggestion}
                            type="button"
                            onClick={() => setCustomPrompt(suggestion)}
                            disabled={isGenerating}
                            className="text-xs bg-white/5 hover:bg-white/10 text-muted-foreground px-3 py-1 rounded-full cursor-pointer transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
                          >
                            {suggestion}
                          </button>
                        ))}
                      </div>
                    </div>
                  </div>

                  {/* Indicateur de streaming */}
                  {isAIGenerating && (
                    <div className="p-3 rounded-lg bg-card border border-primary/20 flex items-center gap-2">
                      <Loader2 className="h-4 w-4 animate-spin text-primary flex-shrink-0" />
                      <p className="flex-1 text-xs text-muted-foreground">
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

                  {/* Résultat généré */}
                  {generatedExercise && !isAIGenerating && (
                    <div className="p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-between gap-3">
                      <div className="flex-1 min-w-0">
                        <p className="text-xs font-semibold text-emerald-400 mb-0.5">
                          {t("aiGenerator.exerciseGenerated")}
                        </p>
                        <p className="text-sm font-medium text-foreground truncate">
                          {generatedExercise.title}
                        </p>
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

          {/* Bouton d'action — dynamique selon le mode */}
          <div className="flex justify-end mt-2">
            <Button
              onClick={handleGenerate}
              disabled={isGenerating}
              size="lg"
              className={cn(
                "btn-cta-primary transition-all",
                isIAEnabled
                  ? "shadow-[0_0_15px_hsl(var(--primary)/0.35)] hover:shadow-[0_0_22px_hsl(var(--primary)/0.5)]"
                  : "shadow-[0_0_14px_hsl(var(--primary)/0.2)]"
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
      </CardContent>
    </Card>
  );
}
