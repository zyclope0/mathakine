'use client';

import { useState } from 'react';
import { useExercises } from '@/hooks/useExercises';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { EXERCISE_TYPES, EXERCISE_TYPE_DISPLAY, DIFFICULTY_LEVELS, DIFFICULTY_DISPLAY } from '@/lib/constants/exercises';
import { Loader2, Sparkles, Zap } from 'lucide-react';
import { useTranslations } from 'next-intl';
import { validateExerciseParams } from '@/lib/validation/exercise';
import { toast } from 'sonner';

export function ExerciseGenerator() {
  const [exerciseType, setExerciseType] = useState<string>(EXERCISE_TYPES.ADDITION);
  const [difficulty, setDifficulty] = useState<string>(DIFFICULTY_LEVELS.INITIE);
  const { generateExercise, isGenerating } = useExercises();
  const t = useTranslations('exercises');

  const handleGenerate = () => {
    // Valider les paramètres avant de générer
    const validation = validateExerciseParams({
      exercise_type: exerciseType,
      difficulty: difficulty,
    });

    if (!validation.isValid) {
      toast.error('Erreur de validation', {
        description: validation.errors.join(', '),
      });
      return;
    }

    generateExercise({
      exercise_type: exerciseType,
      difficulty: difficulty,
      save: true,
    });
  };

  return (
    <Card className="h-full border-primary/20">
      <CardHeader className="pb-2">
        <CardTitle className="flex items-center gap-2 text-sm md:text-base">
          <Zap className="h-4 w-4 text-primary" />
          {t('generator.title')}
        </CardTitle>
        <CardDescription className="text-xs hidden sm:block">
          {t('generator.description')}
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-2 pt-0">
        <div className="grid grid-cols-2 gap-2">
          <div className="space-y-1">
            <label htmlFor="exercise-type-select" className="text-xs font-medium">
              {t('generator.exerciseType')}
            </label>
            <Select value={exerciseType} onValueChange={setExerciseType}>
              <SelectTrigger id="exercise-type-select" className="h-8 text-xs">
                <SelectValue placeholder={t('generator.selectType')} />
              </SelectTrigger>
              <SelectContent>
                {Object.entries(EXERCISE_TYPE_DISPLAY).map(([value, label]) => (
                  <SelectItem key={value} value={value}>
                    {label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-1">
            <label htmlFor="exercise-difficulty-select" className="text-xs font-medium">
              {t('generator.difficulty')}
            </label>
            <Select value={difficulty} onValueChange={setDifficulty}>
              <SelectTrigger id="exercise-difficulty-select" className="h-8 text-xs">
                <SelectValue placeholder={t('generator.selectDifficulty')} />
              </SelectTrigger>
              <SelectContent>
                {Object.entries(DIFFICULTY_DISPLAY).map(([value, label]) => (
                  <SelectItem key={value} value={value}>
                    {label}
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
              {t('generator.generating')}
            </>
          ) : (
            <>
              <Zap className="mr-1.5 h-3.5 w-3.5" />
              {t('generator.generate')}
            </>
          )}
        </Button>
      </CardContent>
    </Card>
  );
}

