'use client';

import { useState, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Loader2, Sparkles, X, AlertCircle } from 'lucide-react';
import { toast } from 'sonner';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { CHALLENGE_TYPES, CHALLENGE_TYPE_DISPLAY, AGE_GROUPS, AGE_GROUP_DISPLAY, type ChallengeType, type AgeGroup } from '@/lib/constants/challenges';
import type { Challenge } from '@/types/api';
import { useQueryClient } from '@tanstack/react-query';
import { useRouter } from 'next/navigation';
import { useTranslations } from 'next-intl';
import { useAuth } from '@/hooks/useAuth';

interface AIGeneratorProps {
  onChallengeGenerated?: (challenge: Challenge) => void;
}

export function AIGenerator({ onChallengeGenerated }: AIGeneratorProps) {
  const [challengeType, setChallengeType] = useState<ChallengeType>(CHALLENGE_TYPES.SEQUENCE);
  const [ageGroup, setAgeGroup] = useState<AgeGroup>(AGE_GROUPS.GROUP_10_12);
  const [customPrompt, setCustomPrompt] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [streamedText, setStreamedText] = useState('');
  const [generatedChallenge, setGeneratedChallenge] = useState<Challenge | null>(null);
  const eventSourceRef = useRef<EventSource | null>(null);
  const queryClient = useQueryClient();
  const router = useRouter();
  const t = useTranslations('challenges');
  const { user, isLoading: isAuthLoading } = useAuth();

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

    // Vérifier l'authentification
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

    setIsGenerating(true);
    setStreamedText('');
    setGeneratedChallenge(null);

    try {
      // Construire l'URL avec les paramètres
      const params = new URLSearchParams({
        challenge_type: challengeType,
        age_group: ageGroup,
      });
      if (customPrompt.trim()) {
        params.append('prompt', customPrompt.trim());
      }

      // Utiliser la route API Next.js qui fait le proxy avec les credentials
      const url = `/api/challenges/generate-ai-stream?${params.toString()}`;

      // Créer l'EventSource pour SSE (via proxy Next.js qui gère les credentials)
      const eventSource = new EventSource(url);
      eventSourceRef.current = eventSource;

      eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);

          if (data.type === 'status') {
            // Message de statut uniquement
            setStreamedText(data.message);
          } else if (data.type === 'challenge') {
            // Challenge complet reçu
            const challenge = data.challenge as Challenge;
            
            // Vérifier que le challenge est valide
            if (!challenge || !challenge.title) {
              console.error('Challenge invalide reçu:', challenge);
              toast.error(t('aiGenerator.error'), {
                description: t('aiGenerator.errorDescription'),
              });
              setStreamedText('');
              eventSource.close();
              setIsGenerating(false);
              eventSourceRef.current = null;
              return;
            }
            
            setGeneratedChallenge(challenge);
            setStreamedText(''); // Nettoyer le message de statut
            eventSource.close();
            setIsGenerating(false);
            eventSourceRef.current = null;

            // Invalider le cache pour recharger la liste
            queryClient.invalidateQueries({ queryKey: ['challenges'] });
            queryClient.invalidateQueries({ queryKey: ['completed-challenges'] });

            toast.success(t('aiGenerator.success'), {
              description: t('aiGenerator.successDescription', { title: challenge.title }),
            });

            // Appeler le callback si fourni
            if (onChallengeGenerated) {
              onChallengeGenerated(challenge);
            }
          } else if (data.type === 'error') {
            setStreamedText(''); // Nettoyer le message de statut
            eventSource.close();
            setIsGenerating(false);
            eventSourceRef.current = null;
            toast.error(t('aiGenerator.error'), {
              description: data.message || t('aiGenerator.errorDescription'),
            });
          } else if (data.type === 'done') {
            // Génération terminée
            setStreamedText('');
            eventSource.close();
            setIsGenerating(false);
            eventSourceRef.current = null;
          }
        } catch (parseError) {
          console.error('Erreur de parsing SSE:', parseError);
        }
      };

      eventSource.onerror = (error) => {
        console.error('Erreur EventSource:', error);
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

  const handleViewChallenge = () => {
    if (generatedChallenge?.id) {
      router.push(`/challenges/${generatedChallenge.id}`);
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
        {/* Sélecteurs de type et groupe d'âge */}
        <div className="grid grid-cols-2 gap-2">
          <div className="space-y-1">
            <label htmlFor="ai-challenge-type" className="block text-xs font-medium text-muted-foreground">
              {t('aiGenerator.challengeType')}
            </label>
            <Select
              value={challengeType}
              onValueChange={(value: ChallengeType) => setChallengeType(value)}
              disabled={isGenerating}
            >
              <SelectTrigger id="ai-challenge-type" className="w-full h-8 text-xs bg-background text-foreground border-primary/30">
                <SelectValue placeholder={t('aiGenerator.selectType')} />
              </SelectTrigger>
              <SelectContent className="bg-card border-primary/30">
                {Object.entries(CHALLENGE_TYPE_DISPLAY).map(([key, value]) => (
                  <SelectItem key={key} value={key} className="text-foreground hover:bg-primary/10">
                    {value}
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
                {Object.entries(AGE_GROUP_DISPLAY).map(([key, value]) => (
                  <SelectItem key={key} value={key} className="text-foreground hover:bg-primary/10">
                    {value}
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
              className="h-6 w-6 p-0"
              aria-label={t('aiGenerator.cancel')}
            >
              <X className="h-3 w-3" />
            </Button>
          </div>
        )}

        {/* Challenge généré */}
        {generatedChallenge && !isGenerating && (
          <div className="p-3 rounded-lg bg-success/10 border border-success/30">
            <p className="text-xs font-medium text-success mb-1">
              {t('aiGenerator.success')}
            </p>
            <p className="text-xs text-muted-foreground mb-2">
              {generatedChallenge.title}
            </p>
            <Button
              onClick={handleViewChallenge}
              size="sm"
              variant="outline"
              className="w-full text-xs"
            >
              {t('aiGenerator.viewChallenge')}
            </Button>
          </div>
        )}

        {/* Message si non authentifié */}
        {!user && !isAuthLoading && (
          <div className="p-3 rounded-lg bg-warning/10 border border-warning/30 flex items-start gap-2">
            <AlertCircle className="h-4 w-4 text-warning mt-0.5 flex-shrink-0" />
            <div className="text-xs text-warning">
              <p className="font-medium mb-1">{t('aiGenerator.authRequired')}</p>
              <p className="text-xs opacity-80">{t('aiGenerator.authRequiredDescription')}</p>
            </div>
          </div>
        )}

        {/* Bouton de génération */}
        <Button
          onClick={handleAIGenerate}
          disabled={isGenerating || !user || isAuthLoading}
          className="w-full bg-primary text-primary-foreground hover:bg-primary/90"
          size="sm"
          title={!user ? t('aiGenerator.authRequired') : undefined}
        >
          {isGenerating ? (
            <>
              <Loader2 className="mr-2 h-3 w-3 animate-spin" />
              {t('aiGenerator.generating')}
            </>
          ) : (
            <>
              <Sparkles className="mr-2 h-3 w-3" />
              {t('aiGenerator.generate')}
            </>
          )}
        </Button>
      </CardContent>
    </Card>
  );
}

