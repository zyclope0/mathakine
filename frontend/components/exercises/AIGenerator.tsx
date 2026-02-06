'use client';

import { useState, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Loader2, Sparkles, X } from 'lucide-react';
import { toast } from 'sonner';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { EXERCISE_TYPES, AGE_GROUPS, type ExerciseType, type AgeGroup } from '@/lib/constants/exercises';
import { useExerciseTranslations } from '@/hooks/useChallengeTranslations';
import type { Exercise } from '@/types/api';
import { useQueryClient } from '@tanstack/react-query';
import { useRouter } from 'next/navigation';
import { useTranslations } from 'next-intl';
import { useAuth } from '@/hooks/useAuth';
import { validateExerciseParams, validateAIPrompt } from '@/lib/validation/exercise';

interface AIGeneratorProps {
  onExerciseGenerated?: (exercise: Exercise) => void;
}

export function AIGenerator({ onExerciseGenerated }: AIGeneratorProps) {
  const [exerciseType, setExerciseType] = useState<ExerciseType>(EXERCISE_TYPES.ADDITION);
  const [ageGroup, setAgeGroup] = useState<AgeGroup>(AGE_GROUPS.GROUP_6_8);
  const [customPrompt, setCustomPrompt] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [streamedText, setStreamedText] = useState('');
  const [generatedExercise, setGeneratedExercise] = useState<Exercise | null>(null);
  const eventSourceRef = useRef<EventSource | null>(null);
  const queryClient = useQueryClient();
  const router = useRouter();
  const t = useTranslations('exercises');
  const { getTypeDisplay, getAgeDisplay } = useExerciseTranslations();
  const { user } = useAuth();

  // Nettoyer l'EventSource lors du démontage
  useEffect(() => {
    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
    };
  }, []);

  const handleAIGenerate = async () => {
    if (isGenerating) return;

    // Vérifier l'authentification côté client
    if (!user) {
      toast.error(t('aiGenerator.authRequired'), {
        description: t('aiGenerator.authRequiredDescription'),
        action: {
          label: t('aiGenerator.login'),
          onClick: () => router.push('/login'),
        },
      });
      return;
    }

    // Valider les paramètres avant de générer
    const validation = validateExerciseParams({
      exercise_type: exerciseType,
      age_group: ageGroup,
    });

    if (!validation.valid) {
      toast.error(t('aiGenerator.validationError'), {
        description: validation.errors.join(', '),
      });
      return;
    }

    // Valider le prompt personnalisé si fourni
    if (customPrompt.trim()) {
      const promptValidation = validateAIPrompt(customPrompt.trim());
      if (!promptValidation.valid) {
        toast.error(t('aiGenerator.promptValidationError'), {
          description: promptValidation.errors.join(', '),
        });
        return;
      }
    }

    setIsGenerating(true);
    setStreamedText('');
    setGeneratedExercise(null);

    try {
      // Construire l'URL avec les paramètres
      const params = new URLSearchParams({
        exercise_type: exerciseType,
        age_group: ageGroup,
      });
      if (customPrompt.trim()) {
        params.append('prompt', customPrompt.trim());
      }

      // Utiliser la route API Next.js qui fait le proxy avec les credentials
      const url = `/api/exercises/generate-ai-stream?${params.toString()}`;

      // Créer l'EventSource pour SSE (via proxy Next.js qui gère les credentials)
      const eventSource = new EventSource(url);
      eventSourceRef.current = eventSource;

      eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);

          if (data.type === 'chunk') {
            // Ne plus afficher les chunks JSON (masqué pour meilleure UX)
            // Le JSON est accumulé en arrière-plan mais pas affiché à l'utilisateur
          } else if (data.type === 'status') {
            // Message de statut uniquement
            setStreamedText(data.message);
          } else if (data.type === 'exercise') {
            // Exercice complet reçu
            const exercise = data.exercise as Exercise;
            setGeneratedExercise(exercise);
            setStreamedText(''); // Nettoyer le message de statut
            eventSource.close();
            setIsGenerating(false);
            eventSourceRef.current = null;

            // Invalider le cache pour recharger la liste
            queryClient.invalidateQueries({ queryKey: ['exercises'] });

            toast.success(t('aiGenerator.success'), {
              description: t('aiGenerator.successDescription', { title: exercise.title }),
            });

            // Appeler le callback si fourni
            if (onExerciseGenerated) {
              onExerciseGenerated(exercise);
            }
          } else if (data.type === 'error') {
            setStreamedText(''); // Nettoyer le message de statut
            eventSource.close();
            setIsGenerating(false);
            eventSourceRef.current = null;
            toast.error(t('aiGenerator.error'), {
              description: data.message || t('aiGenerator.errorDescription'),
            });
          }
        } catch (parseError) {
          // Erreur de parsing SSE - déjà gérée par le toast d'erreur
          // Ne pas logger en production pour éviter les fuites d'information
        }
      };

      eventSource.onerror = (error) => {
        // Erreur EventSource - déjà gérée par le toast d'erreur
        // Ne pas logger en production pour éviter les fuites d'information
        setStreamedText(''); // Nettoyer le message de statut
        eventSource.close();
        setIsGenerating(false);
        eventSourceRef.current = null;
        toast.error(t('aiGenerator.connectionError'), {
          description: t('aiGenerator.connectionErrorDescription'),
        });
      };
    } catch (error) {
      setIsGenerating(false);
      toast.error(t('aiGenerator.startError'), {
        description: t('aiGenerator.startErrorDescription'),
      });
    }
  };

  const handleCancel = () => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }
    setIsGenerating(false);
    setStreamedText('');
  };

  const handleViewExercise = () => {
    if (generatedExercise?.id) {
      router.push(`/exercises/${generatedExercise.id}`);
    }
  };

  return (
    <Card className="h-full bg-card border-primary/20 shadow-lg">
      <CardHeader className="pb-2">
        <CardTitle className="flex items-center text-primary-on-dark text-sm md:text-base">
          <Sparkles className="mr-2 h-4 w-4 text-primary" />
          {t('aiGenerator.title')}
        </CardTitle>
        <CardDescription className="text-xs hidden sm:block">
          {t('aiGenerator.description')}
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-2 pt-0">
        {/* Sélecteurs de type et difficulté */}
        <div className="grid grid-cols-2 gap-2">
          <div className="space-y-1">
            <label htmlFor="ai-exercise-type" className="block text-xs font-medium text-muted-foreground">
              {t('aiGenerator.exerciseType')}
            </label>
            <Select
              value={exerciseType}
              onValueChange={(value: ExerciseType) => setExerciseType(value)}
              disabled={isGenerating}
            >
              <SelectTrigger id="ai-exercise-type" className="w-full h-8 text-xs bg-background text-foreground border-primary/30">
                <SelectValue placeholder={t('aiGenerator.selectType')} />
              </SelectTrigger>
              <SelectContent className="bg-card border-primary/30">
                {Object.values(EXERCISE_TYPES).map((type) => (
                  <SelectItem key={type} value={type} className="text-foreground hover:bg-primary/10">
                    {getTypeDisplay(type)}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-1">
            <label htmlFor="ai-age-group" className="block text-xs font-medium text-muted-foreground">
              {t('aiGenerator.ageGroup')}
            </label>
            <Select
              value={ageGroup}
              onValueChange={(value: AgeGroup) => setAgeGroup(value)}
              disabled={isGenerating}
            >
              <SelectTrigger id="ai-age-group" className="w-full h-8 text-xs bg-background text-foreground border-primary/30">
                <SelectValue placeholder={t('aiGenerator.selectAgeGroup')} />
              </SelectTrigger>
              <SelectContent className="bg-card border-primary/30">
                {Object.values(AGE_GROUPS).map((group) => (
                  <SelectItem key={group} value={group} className="text-foreground hover:bg-primary/10">
                    {getAgeDisplay(group)}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>

        {/* Prompt personnalisé (optionnel) */}
        <div className="space-y-1">
          <label htmlFor="ai-prompt" className="block text-xs font-medium text-muted-foreground">
            {t('aiGenerator.customPrompt')}
          </label>
          <textarea
            id="ai-prompt"
            value={customPrompt}
            onChange={(e) => setCustomPrompt(e.target.value)}
            placeholder={t('aiGenerator.customPromptPlaceholder')}
            className="w-full p-2 text-xs rounded-lg bg-background text-foreground border border-primary/30 min-h-[60px] resize-none focus:outline-none focus:ring-2 focus:ring-primary/50"
            disabled={isGenerating}
          />
        </div>

        {/* Affichage du streaming - Indicateur simple */}
        {isGenerating && (
          <div className="p-3 rounded-lg bg-card border border-primary/20 relative flex items-center gap-2">
            <div className="flex-shrink-0">
              <Loader2 className="h-4 w-4 animate-spin text-primary" />
            </div>
            <div className="flex-1">
              <p className="text-xs text-muted-foreground">
                {streamedText || t('aiGenerator.generating')}
              </p>
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={handleCancel}
              className="h-6 w-6 p-0 flex-shrink-0"
              aria-label={t('aiGenerator.cancelGeneration')}
            >
              <X className="h-3 w-3" />
            </Button>
          </div>
        )}

        {/* Exercice généré */}
        {generatedExercise && (
          <div className="p-2 rounded-lg bg-success/10 border border-success/20">
            <div className="flex items-start justify-between mb-1">
              <p className="font-semibold text-success text-xs">{t('aiGenerator.exerciseGenerated')}</p>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => {
                  setGeneratedExercise(null);
                  setStreamedText('');
                }}
                className="h-6 w-6 p-0"
                aria-label={t('aiGenerator.close')}
              >
                <X className="h-3 w-3" />
              </Button>
            </div>
            <p className="text-foreground font-medium text-xs mb-0.5">{generatedExercise.title}</p>
            <p className="text-muted-foreground text-xs mb-1.5 line-clamp-2">{generatedExercise.question}</p>
            {generatedExercise.id && (
              <Button onClick={handleViewExercise} size="sm" className="w-full h-7 text-xs">
                {t('aiGenerator.viewExercise')}
              </Button>
            )}
          </div>
        )}

        {/* Bouton de génération */}
        <Button
          onClick={handleAIGenerate}
          disabled={isGenerating}
          className="btn-cta-primary w-full h-8 text-xs"
        >
          {isGenerating ? (
            <>
              <Loader2 className="mr-1.5 h-3.5 w-3.5 animate-spin" />
              {t('aiGenerator.generating')}
            </>
          ) : (
            <>
              <Sparkles className="mr-1.5 h-3.5 w-3.5" />
              {t('aiGenerator.generate')}
            </>
          )}
        </Button>

        {isGenerating && (
          <Button
            variant="outline"
            onClick={handleCancel}
            className="w-full h-7 text-xs"
            disabled={!isGenerating}
          >
            <X className="mr-1.5 h-3.5 w-3.5" />
            {t('aiGenerator.cancel')}
          </Button>
        )}
      </CardContent>
    </Card>
  );
}

