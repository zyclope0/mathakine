"use client";

import { useState } from "react";
import { useExercises } from "@/hooks/useExercises";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { EXERCISE_TYPES, AGE_GROUPS } from "@/lib/constants/exercises";
import { useExerciseTranslations } from "@/hooks/useChallengeTranslations";
import { Loader2, Sparkles, Zap } from "lucide-react";
import { useTranslations } from "next-intl";
import { validateExerciseParams } from "@/lib/validation/exercise";
import { toast } from "sonner";

export function ExerciseGenerator() {
  const [exerciseType, setExerciseType] = useState<string>(EXERCISE_TYPES.ADDITION);
  const [ageGroup, setAgeGroup] = useState<string>(AGE_GROUPS.GROUP_6_8);
  const { generateExercise, isGenerating } = useExercises();
  const t = useTranslations("exercises");
  const { getTypeDisplay, getAgeDisplay } = useExerciseTranslations();

  const handleGenerate = () => {
    // Valider les paramètres avant de générer
    const validation = validateExerciseParams({
      exercise_type: exerciseType,
      age_group: ageGroup,
    });

    if (!validation.valid) {
      toast.error("Erreur de validation", {
        description: validation.errors.join(", "),
      });
      return;
    }

    generateExercise({
      exercise_type: exerciseType,
      age_group: ageGroup,
      save: true,
    });
  };

  return (
    <Card className="h-full border-primary/20">
      <CardHeader className="pb-2">
        <CardTitle className="flex items-center gap-2 text-sm md:text-base">
          <Zap className="h-4 w-4 text-primary" />
          {t("generator.title")}
        </CardTitle>
        <CardDescription className="text-xs hidden sm:block">
          {t("generator.description")}
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-2 pt-0">
        <div className="grid grid-cols-2 gap-2">
          <div className="space-y-1">
            <label htmlFor="exercise-type-select" className="text-xs font-medium">
              {t("generator.exerciseType")}
            </label>
            <Select value={exerciseType} onValueChange={setExerciseType}>
              <SelectTrigger id="exercise-type-select" className="h-8 text-xs">
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

          <div className="space-y-1">
            <label htmlFor="exercise-age-group-select" className="text-xs font-medium">
              {t("generator.ageGroup")}
            </label>
            <Select value={ageGroup} onValueChange={setAgeGroup}>
              <SelectTrigger id="exercise-age-group-select" className="h-8 text-xs">
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

        <Button
          onClick={handleGenerate}
          disabled={isGenerating}
          className="btn-cta-primary w-full h-8 text-xs"
        >
          {isGenerating ? (
            <>
              <Loader2 className="mr-1.5 h-3.5 w-3.5 animate-spin" />
              {t("generator.generating")}
            </>
          ) : (
            <>
              <Zap className="mr-1.5 h-3.5 w-3.5" />
              {t("generator.generate")}
            </>
          )}
        </Button>
      </CardContent>
    </Card>
  );
}
